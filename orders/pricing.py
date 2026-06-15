from dataclasses import dataclass
from decimal import Decimal

from promotions.services import (
    calculate_discount,
    coupon_grants_free_shipping,
    get_coupon_by_code,
    validate_coupon,
)
from shipping.services import calculate_shipping_amount


@dataclass
class OrderTotals:
    subtotal_amount: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    coupon_code: str
    coupon: object
    shipping_label: str
    coupon_error: str = ""

    @property
    def merchandise_total(self):
        return max(self.subtotal_amount - self.discount_amount, Decimal("0.00"))


def get_line_unit_price(product, variant=None):
    if variant is not None:
        if variant.discounted_price is not None:
            return variant.discounted_price
        if variant.price is not None:
            return variant.price

    if product.discounted_price is not None:
        return product.discounted_price

    return product.price


def get_line_total(cart_line):
    return get_line_unit_price(cart_line.product, getattr(cart_line, "variant", None)) * cart_line.quantity


def compute_order_totals(
    cart_lines,
    *,
    coupon_code=None,
    pincode=None,
    state=None,
):
    subtotal = sum((get_line_total(line) for line in cart_lines), Decimal("0.00"))
    coupon = get_coupon_by_code(coupon_code) if coupon_code else None
    coupon_error = ""

    if coupon_code and coupon is None:
        coupon_error = "Coupon not found."
        coupon_code = ""

    if coupon:
        valid, coupon_error = validate_coupon(coupon, subtotal)

        if not valid:
            coupon = None
            coupon_code = ""

    discount_amount = calculate_discount(coupon, subtotal) if coupon else Decimal("0.00")
    merchandise_total = max(subtotal - discount_amount, Decimal("0.00"))
    force_free_shipping = coupon_grants_free_shipping(coupon, subtotal) if coupon else False

    shipping_amount, shipping_label = calculate_shipping_amount(
        merchandise_total,
        state=state or "",
        pincode=pincode or "",
        force_free=force_free_shipping,
    )

    total_amount = merchandise_total + shipping_amount

    return OrderTotals(
        subtotal_amount=subtotal,
        discount_amount=discount_amount,
        shipping_amount=shipping_amount,
        total_amount=total_amount,
        coupon_code=coupon_code or "",
        coupon=coupon,
        shipping_label=shipping_label,
        coupon_error=coupon_error,
    )
