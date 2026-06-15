from django.db import transaction

from products.inventory import restore_stock_for_order

from .emails import send_admin_order_cancelled, send_order_cancellation
from .models import Order

CANCELLABLE_STATUSES = {"pending", "processing"}


def can_cancel_order(order):
    if order.status == "cancelled":
        return False

    if order.status in ("shipped", "delivered"):
        return False

    return order.status in CANCELLABLE_STATUSES


@transaction.atomic
def cancel_order(order):
    order = Order.objects.select_for_update().get(pk=order.pk)

    if not can_cancel_order(order):
        return False, "This order can no longer be cancelled."

    if order.payment_status == "paid":
        restore_stock_for_order(order)

    order.status = "cancelled"
    order.save(update_fields=["status"])

    send_order_cancellation(order)
    send_admin_order_cancelled(order)

    return True, "Your order has been cancelled."
