from django.db import transaction
from django.db.models import F

from products.models import Product

from .emails import send_admin_order_cancelled, send_order_cancellation
from .models import Order

CANCELLABLE_STATUSES = {"pending", "processing"}


def can_cancel_order(order):
    if order.status == "cancelled":
        return False

    if order.status in ("shipped", "delivered"):
        return False

    return order.status in CANCELLABLE_STATUSES


def restore_stock_for_order(order):
    if order.payment_status != "paid":
        return

    for item in order.items.select_related("product"):
        product = item.product

        Product.objects.filter(pk=product.pk).update(
            stock=F("stock") + item.quantity,
        )

        product.refresh_from_db()

        if product.status == "out_of_stock" and product.stock > 0:
            product.status = "published"
            product.save(update_fields=["status"])


@transaction.atomic
def cancel_order(order):
    order = Order.objects.select_for_update().get(pk=order.pk)

    if not can_cancel_order(order):
        return False, "This order can no longer be cancelled."

    restore_stock_for_order(order)

    order.status = "cancelled"
    order.save(update_fields=["status"])

    send_order_cancellation(order)
    send_admin_order_cancelled(order)

    return True, "Your order has been cancelled."
