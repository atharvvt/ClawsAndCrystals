from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from orders.pricing import compute_order_totals
from products.inventory import can_increase_quantity, is_purchasable, validate_cart_stock
from products.models import Product, ProductVariant
from promotions.services import get_coupon_by_code, validate_coupon

from .models import CartItem
from .session_cart import (
    add_to_session_cart,
    remove_from_session_cart,
    set_session_cart_quantity,
)
from .utils import (
    clear_applied_coupon_code,
    get_applied_coupon_code,
    get_cart_lines,
    set_applied_coupon_code,
)


def _resolve_variant(product, variant_id):
    if variant_id:
        return get_object_or_404(ProductVariant, pk=variant_id, product=product)

    if product.has_variants:
        return product.variants.filter(is_default=True).first() or product.variants.first()

    return None


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.GET.get("variant")

    if product.status != "published":
        messages.error(request, "This product is not available.")
        return redirect(request.META.get("HTTP_REFERER", "product_list"))

    variant = _resolve_variant(product, variant_id)

    if not is_purchasable(product, variant):
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(request.META.get("HTTP_REFERER", "product_list"))

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            variant=variant,
            defaults={"quantity": 0},
        )

        if created or cart_item.quantity == 0:
            cart_item.quantity = 1
            cart_item.save()
        elif can_increase_quantity(product, cart_item.quantity, variant=variant):
            cart_item.quantity += 1
            cart_item.save()
        else:
            stock = variant.stock if variant else product.stock
            messages.warning(
                request,
                f"Only {stock} of {product.name} available in stock.",
            )
    else:
        add_to_session_cart(
            request.session,
            product.id,
            variant.id if variant else None,
            quantity=1,
        )

    return redirect("cart")


def cart_view(request):
    cart_lines = get_cart_lines(request)
    stock_errors = validate_cart_stock(cart_lines)
    coupon_code = get_applied_coupon_code(request)
    totals = compute_order_totals(cart_lines, coupon_code=coupon_code)

    if coupon_code and totals.coupon_error:
        clear_applied_coupon_code(request)
        messages.warning(request, totals.coupon_error)

    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_lines,
            "totals": totals,
            "stock_errors": stock_errors,
            "coupon_code": totals.coupon_code,
        },
    )


@require_POST
def apply_coupon_view(request):
    code = request.POST.get("coupon_code", "").strip()
    cart_lines = get_cart_lines(request)
    subtotal = sum(line.total_price for line in cart_lines)
    coupon = get_coupon_by_code(code)

    if coupon is None:
        messages.error(request, "Coupon not found.")
        return redirect("cart")

    valid, error = validate_coupon(coupon, subtotal)

    if not valid:
        messages.error(request, error)
        return redirect("cart")

    set_applied_coupon_code(request, coupon.code)
    messages.success(request, f"Coupon {coupon.code} applied.")
    return redirect("cart")


@require_POST
def remove_coupon_view(request):
    clear_applied_coupon_code(request)
    messages.info(request, "Coupon removed.")
    return redirect("cart")


def remove_from_cart(request, item_id):
    if request.user.is_authenticated and not str(item_id).startswith("session:"):
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        item.delete()
    else:
        key = str(item_id).replace("session:", "")
        parts = key.split(":")
        product_id = int(parts[0])
        variant_id = int(parts[1]) if len(parts) > 1 and parts[1] != "0" else None
        remove_from_session_cart(request.session, product_id, variant_id)

    return redirect("cart")


def increase_quantity(request, item_id):
    if request.user.is_authenticated and not str(item_id).startswith("session:"):
        item = get_object_or_404(CartItem, id=item_id, user=request.user)

        if can_increase_quantity(item.product, item.quantity, variant=item.variant):
            item.quantity += 1
            item.save()
        else:
            stock = item.variant.stock if item.variant else item.product.stock
            messages.warning(
                request,
                f"Only {stock} of {item.product.name} available in stock.",
            )
    else:
        key = str(item_id).replace("session:", "")
        parts = key.split(":")
        product_id = int(parts[0])
        variant_id = int(parts[1]) if len(parts) > 1 and parts[1] != "0" else None
        product = get_object_or_404(Product, pk=product_id)
        variant = _resolve_variant(product, variant_id)

        from .session_cart import get_session_cart

        cart = get_session_cart(request.session)
        for line in cart:
            if line["product_id"] == product_id and line.get("variant_id") == (variant.id if variant else None):
                if can_increase_quantity(product, line["quantity"], variant=variant):
                    set_session_cart_quantity(
                        request.session,
                        product_id,
                        variant.id if variant else None,
                        line["quantity"] + 1,
                    )
                else:
                    stock = variant.stock if variant else product.stock
                    messages.warning(
                        request,
                        f"Only {stock} of {product.name} available in stock.",
                    )
                break

    return redirect("cart")


def decrease_quantity(request, item_id):
    if request.user.is_authenticated and not str(item_id).startswith("session:"):
        item = get_object_or_404(CartItem, id=item_id, user=request.user)

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    else:
        key = str(item_id).replace("session:", "")
        parts = key.split(":")
        product_id = int(parts[0])
        variant_id = int(parts[1]) if len(parts) > 1 and parts[1] != "0" else None

        from .session_cart import get_session_cart

        cart = get_session_cart(request.session)
        for line in cart:
            if line["product_id"] == product_id and line.get("variant_id") == variant_id:
                new_qty = line["quantity"] - 1
                set_session_cart_quantity(
                    request.session,
                    product_id,
                    variant_id,
                    new_qty,
                )
                break

    return redirect("cart")
