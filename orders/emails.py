from django.conf import settings

from config.emails import admin_recipients, send_templated_email, user_wants_order_updates


def _order_context(order):
    return {
        "order": order,
        "items": order.items.select_related("product"),
        "order_url": f"{settings.SITE_URL}/orders/my-orders/{order.id}/",
    }


def send_order_confirmation(order):
    if not user_wants_order_updates(order.user):
        return False

    return send_templated_email(
        subject=f"Order #{order.id} confirmed — {settings.SITE_NAME}",
        template_name="order_confirmation",
        context=_order_context(order),
        recipient_list=[order.email],
    )


def send_order_cancellation(order):
    if not user_wants_order_updates(order.user):
        return False

    return send_templated_email(
        subject=f"Order #{order.id} cancelled — {settings.SITE_NAME}",
        template_name="order_cancellation",
        context=_order_context(order),
        recipient_list=[order.email],
    )


def send_admin_order_cancelled(order):
    recipients = admin_recipients()

    if not recipients:
        return False

    return send_templated_email(
        subject=f"Order #{order.id} cancelled by customer",
        template_name="admin_order_cancelled",
        context=_order_context(order),
        recipient_list=recipients,
    )


def send_admin_new_order(order):
    recipients = admin_recipients()

    if not recipients:
        return False

    return send_templated_email(
        subject=f"New paid order #{order.id} — ₹{order.total_amount}",
        template_name="admin_new_order",
        context=_order_context(order),
        recipient_list=recipients,
    )


def send_order_status_update(order, old_status):
    if order.payment_status != "paid":
        return False

    if not user_wants_order_updates(order.user):
        return False

    if order.status == old_status:
        return False

    notify_statuses = {"shipped", "delivered"}

    if order.status not in notify_statuses:
        return False

    return send_templated_email(
        subject=f"Order #{order.id} is now {order.get_status_display()}",
        template_name="order_status_update",
        context={
            **_order_context(order),
            "old_status": old_status,
            "new_status": order.status,
            "new_status_display": order.get_status_display(),
        },
        recipient_list=[order.email],
    )
