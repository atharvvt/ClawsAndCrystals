import json
import logging

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import ShippingAddress
from cart.utils import (
    clear_applied_coupon_code,
    get_applied_coupon_code,
    get_cart_lines,
)
from products.inventory import build_variant_label, get_unit_price, validate_cart_stock
from reviews.eligibility import get_reviewable_items_for_order

from .cancellation import can_cancel_order, cancel_order
from .forms import CheckoutForm
from .models import Order, OrderItem
from .payments import (
    RazorpayConfigError,
    amount_in_paise,
    create_razorpay_order,
    handle_webhook_event,
    mark_order_paid,
    verify_payment_signature,
    verify_webhook_signature,
)
from .pricing import compute_order_totals

logger = logging.getLogger(__name__)


def _create_order_from_cart(user, form_data, cart_lines, totals):
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            full_name=form_data["full_name"],
            email=form_data["email"],
            phone=form_data["phone"],
            address=form_data["address"],
            city=form_data["city"],
            state=form_data["state"],
            pincode=form_data["pincode"],
            subtotal_amount=totals.subtotal_amount,
            discount_amount=totals.discount_amount,
            shipping_amount=totals.shipping_amount,
            total_amount=totals.total_amount,
            coupon_code=totals.coupon_code,
            applied_coupon=totals.coupon,
        )

        for line in cart_lines:
            price = get_unit_price(line.product, getattr(line, "variant", None))
            variant = getattr(line, "variant", None)

            OrderItem.objects.create(
                order=order,
                product=line.product,
                variant=variant,
                variant_label=build_variant_label(variant),
                quantity=line.quantity,
                price=price,
            )

        if totals.coupon:
            totals.coupon.used_count += 1
            totals.coupon.save(update_fields=["used_count"])

    return order


def _ensure_razorpay_order(order):
    if order.razorpay_order_id:
        return order

    razorpay_order = create_razorpay_order(order)
    order.razorpay_order_id = razorpay_order["id"]
    order.save(update_fields=["razorpay_order_id"])

    return order


def _payment_error_message(exc):
    if isinstance(exc, RazorpayConfigError):
        return str(exc)

    if isinstance(exc, razorpay.errors.BadRequestError):
        message = str(exc)

        if "Authentication failed" in message:
            return (
                "Razorpay authentication failed. Check RAZORPAY_KEY_ID and "
                "RAZORPAY_KEY_SECRET in your .env file match your test keys."
            )

        return f"Payment gateway error: {message}"

    return "Unable to initiate payment. Please try again."


def _handle_razorpay_order_failure(request, order, exc):
    logger.exception("Failed to create Razorpay order for order %s", order.id)
    order.delete()
    messages.error(request, _payment_error_message(exc))


def _save_shipping_address(user, form_data):
    if not form_data.get("save_address"):
        return

    address_fields = {
        "full_name": form_data["full_name"],
        "email": form_data["email"],
        "phone": form_data["phone"],
        "address": form_data["address"],
        "city": form_data["city"],
        "state": form_data["state"],
        "pincode": form_data["pincode"],
    }

    existing = ShippingAddress.objects.filter(
        user=user,
        **address_fields,
    ).first()

    if existing:
        if form_data.get("address_label"):
            existing.label = form_data["address_label"]
            existing.save(update_fields=["label"])
        return existing

    has_default = ShippingAddress.objects.filter(
        user=user,
        is_default=True,
    ).exists()

    return ShippingAddress.objects.create(
        user=user,
        label=form_data.get("address_label") or "Home",
        is_default=not has_default,
        **address_fields,
    )


def _checkout_initial(user, selected_address=None):
    if selected_address:
        return selected_address.to_form_initial()

    default_address = ShippingAddress.objects.filter(
        user=user,
        is_default=True,
    ).first()

    if default_address:
        return default_address.to_form_initial()

    initial = {}

    if user.email:
        initial["email"] = user.email

    if user.get_full_name():
        initial["full_name"] = user.get_full_name()
    else:
        initial["full_name"] = user.username

    return initial


@login_required
def checkout_view(request):
    cart_lines = get_cart_lines(request)

    if not cart_lines:
        return redirect("cart")

    stock_errors = validate_cart_stock(cart_lines)

    if stock_errors:
        for error in stock_errors:
            messages.error(request, error)
        return redirect("cart")

    coupon_code = get_applied_coupon_code(request)
    saved_addresses = ShippingAddress.objects.filter(user=request.user)
    selected_address = None
    use_address_id = request.GET.get("use_address")

    if use_address_id:
        selected_address = saved_addresses.filter(id=use_address_id).first()

    pincode = ""
    state = ""

    if selected_address:
        pincode = selected_address.pincode
        state = selected_address.state

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            pincode = form.cleaned_data["pincode"]
            state = form.cleaned_data["state"]
            totals = compute_order_totals(
                cart_lines,
                coupon_code=coupon_code,
                pincode=pincode,
                state=state,
            )

            if coupon_code and totals.coupon_error:
                clear_applied_coupon_code(request)
                messages.warning(request, totals.coupon_error)
                return redirect("cart")

            _save_shipping_address(request.user, form.cleaned_data)

            order = _create_order_from_cart(
                request.user,
                form.cleaned_data,
                cart_lines,
                totals,
            )

            clear_applied_coupon_code(request)

            try:
                _ensure_razorpay_order(order)
            except Exception as exc:
                _handle_razorpay_order_failure(request, order, exc)
                return redirect("checkout")

            return redirect("payment", order_id=order.id)
    else:
        form = CheckoutForm(
            initial=_checkout_initial(request.user, selected_address),
        )

    totals = compute_order_totals(
        cart_lines,
        coupon_code=coupon_code,
        pincode=pincode,
        state=state,
    )

    return render(
        request,
        "orders/checkout.html",
        {
            "cart_items": cart_lines,
            "totals": totals,
            "coupon_code": totals.coupon_code,
            "form": form,
            "saved_addresses": saved_addresses,
            "selected_address": selected_address,
        },
    )


@login_required
def payment_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    if order.payment_status == "paid":
        return redirect("order_success", order_id=order.id)

    try:
        order = _ensure_razorpay_order(order)
    except Exception as exc:
        messages.error(request, _payment_error_message(exc))
        return redirect("my_orders")

    return render(
        request,
        "orders/payment.html",
        {
            "order": order,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": order.razorpay_order_id,
            "amount_paise": amount_in_paise(order.total_amount),
        },
    )


@login_required
@require_POST
def payment_verify_view(request):
    payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")

    if not all([payment_id, razorpay_order_id, signature]):
        messages.error(request, "Invalid payment response.")
        return redirect("cart")

    order = get_object_or_404(
        Order,
        razorpay_order_id=razorpay_order_id,
        user=request.user,
    )

    if order.payment_status == "paid":
        return redirect("order_success", order_id=order.id)

    try:
        verify_payment_signature(payment_id, razorpay_order_id, signature)
    except Exception:
        logger.exception("Payment signature verification failed for order %s", order.id)
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])
        messages.error(request, "Payment verification failed. Please try again.")
        return redirect("payment", order_id=order.id)

    mark_order_paid(order, payment_id, signature)
    messages.success(request, "Payment successful! Your order has been confirmed.")
    return redirect("order_success", order_id=order.id)


@csrf_exempt
@require_POST
def razorpay_webhook_view(request):
    signature = request.headers.get("X-Razorpay-Signature", "")

    try:
        verify_webhook_signature(request.body, signature)
    except Exception:
        logger.exception("Webhook signature verification failed")
        return HttpResponseBadRequest("Invalid signature")

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    handle_webhook_event(payload)
    return HttpResponse(status=200)


@login_required
def retry_payment_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        payment_status="unpaid",
    )

    order.razorpay_order_id = None
    order.save(update_fields=["razorpay_order_id"])

    return redirect("payment", order_id=order.id)


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        payment_status="paid",
    )

    return render(
        request,
        "orders/success.html",
        {
            "order": order,
        },
    )


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(
        user=request.user,
    ).order_by("-created_at")

    orders_data = [
        {
            "order": order,
            "reviewable_items": get_reviewable_items_for_order(request.user, order),
        }
        for order in orders
    ]

    return render(
        request,
        "orders/my_orders.html",
        {
            "orders_data": orders_data,
        },
    )


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    reviewable_items = get_reviewable_items_for_order(request.user, order)
    reviewable_product_ids = {item.product_id for item in reviewable_items}

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
            "can_cancel": can_cancel_order(order),
            "reviewable_items": reviewable_items,
            "reviewable_product_ids": reviewable_product_ids,
        },
    )


@login_required
@require_POST
def cancel_order_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    success, message = cancel_order(order)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect("order_detail", order_id=order.id)
