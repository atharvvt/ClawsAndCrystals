from decimal import Decimal

from .models import Coupon


def get_coupon_by_code(code):
    if not code:
        return None

    try:
        return Coupon.objects.get(code=code.upper().strip())
    except Coupon.DoesNotExist:
        return None


def validate_coupon(coupon, subtotal):
    if coupon is None:
        return False, "Coupon not found."

    if not coupon.is_valid():
        return False, "This coupon is no longer valid."

    if subtotal < coupon.min_order_amount:
        return False, f"Minimum order of ₹{coupon.min_order_amount} required for this coupon."

    return True, ""


def calculate_discount(coupon, subtotal):
    if coupon is None:
        return Decimal("0.00")

    valid, _ = validate_coupon(coupon, subtotal)

    if not valid:
        return Decimal("0.00")

    if coupon.coupon_type == Coupon.TYPE_PERCENT:
        return (subtotal * coupon.value / Decimal("100")).quantize(Decimal("0.01"))

    if coupon.coupon_type == Coupon.TYPE_FIXED:
        return min(coupon.value, subtotal)

    return Decimal("0.00")


def coupon_grants_free_shipping(coupon, subtotal):
    if coupon is None or coupon.coupon_type != Coupon.TYPE_FREE_SHIPPING:
        return False

    valid, _ = validate_coupon(coupon, subtotal)

    if not valid:
        return False

    return subtotal >= coupon.free_shipping_min
