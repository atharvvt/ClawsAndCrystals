from products.models import Product, ProductVariant

from .lines import SessionCartLine
from .models import CartItem
from .session_cart import (
    SESSION_CART_KEY,
    clear_session_cart,
    get_session_cart,
    get_session_cart_count,
    get_session_coupon_code,
    set_session_coupon_code,
)


def get_cart_lines(request):
    if request.user.is_authenticated:
        return list(
            CartItem.objects.filter(user=request.user).select_related(
                "product",
                "variant",
            )
        )

    lines = []

    for entry in get_session_cart(request.session):
        try:
            product = Product.objects.get(pk=entry["product_id"])
        except Product.DoesNotExist:
            continue

        variant = None
        variant_id = entry.get("variant_id")

        if variant_id:
            variant = ProductVariant.objects.filter(
                pk=variant_id,
                product=product,
            ).first()

        lines.append(
            SessionCartLine(
                product=product,
                variant=variant,
                quantity=entry.get("quantity", 1),
                session_key=_line_key(product.id, variant.id if variant else None),
            )
        )

    return lines


def _line_key(product_id, variant_id):
    return f"session:{product_id}:{variant_id or 0}"


def get_cart_count(request):
    if request.user.is_authenticated:
        return sum(
            item.quantity
            for item in CartItem.objects.filter(user=request.user).only("quantity")
        )

    return get_session_cart_count(request.session)


def get_applied_coupon_code(request):
    return get_session_coupon_code(request.session)


def set_applied_coupon_code(request, code):
    set_session_coupon_code(request.session, code)


def clear_applied_coupon_code(request):
    set_session_coupon_code(request.session, "")


def merge_session_cart_into_user(request):
    if not request.user.is_authenticated:
        return

    from products.inventory import can_increase_quantity, is_purchasable

    session_cart = get_session_cart(request.session)

    for entry in session_cart:
        try:
            product = Product.objects.get(pk=entry["product_id"])
        except Product.DoesNotExist:
            continue

        variant = None
        variant_id = entry.get("variant_id")

        if variant_id:
            variant = ProductVariant.objects.filter(
                pk=variant_id,
                product=product,
            ).first()

        if not is_purchasable(product, variant):
            continue

        quantity = entry.get("quantity", 1)
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            variant=variant,
            defaults={"quantity": 0},
        )

        desired_qty = cart_item.quantity + quantity if not created else quantity
        max_qty = desired_qty

        while max_qty > 0 and not can_increase_quantity(
            product,
            max_qty - 1,
            variant=variant,
        ):
            max_qty -= 1

        if max_qty <= 0:
            cart_item.delete()
            continue

        cart_item.quantity = max_qty
        cart_item.save()

    clear_session_cart(request.session)
