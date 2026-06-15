from decimal import Decimal

from django.db.models import F

from orders.pricing import get_line_unit_price

from .models import Product, ProductVariant


def available_stock(product, variant=None):
    if variant is not None:
        return variant.stock
    return product.stock


def is_purchasable(product, variant=None):
    stock = available_stock(product, variant)
    return product.status == "published" and stock > 0


def can_increase_quantity(product, current_qty, add=1, variant=None):
    return current_qty + add <= available_stock(product, variant)


def validate_cart_stock(cart_lines):
    errors = []

    for line in cart_lines:
        product = line.product
        variant = getattr(line, "variant", None)
        stock = available_stock(product, variant)

        if stock == 0:
            errors.append(f"{product.name} is out of stock.")
        elif line.quantity > stock:
            errors.append(
                f"{product.name} only has {stock} in stock "
                f"(your cart has {line.quantity})."
            )

    return errors


def _decrement_variant_stock(variant, quantity):
    ProductVariant.objects.filter(pk=variant.pk).update(
        stock=F("stock") - quantity,
    )
    variant.refresh_from_db()
    previous_stock = variant.stock + quantity

    if variant.stock <= 0:
        variant.stock = 0
        variant.save(update_fields=["stock"])

    if previous_stock == 0 and variant.stock > 0:
        from .stock_notify import send_back_in_stock_notifications

        send_back_in_stock_notifications(variant.product, variant)

    return variant


def _decrement_product_stock(product, quantity):
    Product.objects.filter(pk=product.pk).update(
        stock=F("stock") - quantity,
    )
    product.refresh_from_db()
    previous_stock = product.stock + quantity

    if product.stock <= 0:
        product.stock = 0
        product.status = "out_of_stock"
        product.save(update_fields=["stock", "status"])
    elif product.stock <= 5:
        from products.emails import send_low_stock_alert

        send_low_stock_alert(product)

    if previous_stock == 0 and product.stock > 0:
        from .stock_notify import send_back_in_stock_notifications

        send_back_in_stock_notifications(product, None)

    return product


def decrement_stock_for_order(order):
    for item in order.items.select_related("product", "variant"):
        if item.variant_id:
            _decrement_variant_stock(item.variant, item.quantity)
        else:
            _decrement_product_stock(item.product, item.quantity)


def _restore_variant_stock(variant, quantity):
    previous_stock = variant.stock
    ProductVariant.objects.filter(pk=variant.pk).update(
        stock=F("stock") + quantity,
    )
    variant.refresh_from_db()

    if previous_stock == 0 and variant.stock > 0:
        from .stock_notify import send_back_in_stock_notifications

        send_back_in_stock_notifications(variant.product, variant)


def _restore_product_stock(product, quantity):
    previous_stock = product.stock
    Product.objects.filter(pk=product.pk).update(
        stock=F("stock") + quantity,
    )
    product.refresh_from_db()

    if product.status == "out_of_stock" and product.stock > 0:
        product.status = "published"
        product.save(update_fields=["status"])

    if previous_stock == 0 and product.stock > 0:
        from .stock_notify import send_back_in_stock_notifications

        send_back_in_stock_notifications(product, None)


def restore_stock_for_order(order):
    for item in order.items.select_related("product", "variant"):
        if item.variant_id:
            _restore_variant_stock(item.variant, item.quantity)
        else:
            _restore_product_stock(item.product, item.quantity)


def build_variant_label(variant):
    if variant is None:
        return ""
    return variant.display_label


def get_unit_price(product, variant=None):
    return get_line_unit_price(product, variant)
