from django.db.models import F

from .models import Product


def available_stock(product):
    return product.stock


def is_purchasable(product):
    return product.status == "published" and product.stock > 0


def can_increase_quantity(product, current_qty, add=1):
    return current_qty + add <= available_stock(product)


def validate_cart_stock(cart_items):
    errors = []

    for item in cart_items:
        product = item.product
        stock = available_stock(product)

        if stock == 0:
            errors.append(f"{product.name} is out of stock.")
        elif item.quantity > stock:
            errors.append(
                f"{product.name} only has {stock} in stock "
                f"(your cart has {item.quantity})."
            )

    return errors


def decrement_stock_for_order(order):
    for item in order.items.select_related("product"):
        product = item.product

        Product.objects.filter(pk=product.pk).update(
            stock=F("stock") - item.quantity,
        )

        product.refresh_from_db()

        if product.stock <= 0:
            product.stock = 0
            product.status = "out_of_stock"
            product.save(update_fields=["stock", "status"])
        elif product.stock <= 5:
            from products.emails import send_low_stock_alert

            send_low_stock_alert(product)
