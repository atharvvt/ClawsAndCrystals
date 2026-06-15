import logging
from decimal import Decimal

import razorpay
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from cart.models import CartItem

logger = logging.getLogger(__name__)


class RazorpayConfigError(Exception):
    """Raised when Razorpay credentials are missing or invalid."""


def validate_razorpay_config():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise RazorpayConfigError(
            "Razorpay API keys are not configured. "
            "Copy .env.example to .env and add your test keys from "
            "https://dashboard.razorpay.com/app/keys"
        )

    if settings.RAZORPAY_KEY_ID == "rzp_test_your_key_id":
        raise RazorpayConfigError(
            "Razorpay API keys are still set to placeholder values in .env."
        )


def get_razorpay_client():
    validate_razorpay_config()

    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def amount_in_paise(amount):
    return int(Decimal(amount) * 100)


def create_razorpay_order(order):
    client = get_razorpay_client()

    razorpay_order = client.order.create(
        {
            "amount": amount_in_paise(order.total_amount),
            "currency": "INR",
            "receipt": f"order_{order.id}",
            "notes": {
                "django_order_id": str(order.id),
            },
        }
    )

    return razorpay_order


def verify_payment_signature(payment_id, razorpay_order_id, signature):
    client = get_razorpay_client()

    client.utility.verify_payment_signature(
        {
            "razorpay_payment_id": payment_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": signature,
        }
    )


def verify_webhook_signature(body, signature):
    client = get_razorpay_client()

    client.utility.verify_webhook_signature(
        body,
        signature,
        settings.RAZORPAY_WEBHOOK_SECRET,
    )


@transaction.atomic
def mark_order_paid(order, payment_id, signature=""):
    order = order.__class__.objects.select_for_update().get(pk=order.pk)

    if order.payment_status == "paid":
        return False

    order.payment_status = "paid"
    order.status = "processing"
    order.razorpay_payment_id = payment_id

    if signature:
        order.razorpay_signature = signature

    order.paid_at = timezone.now()
    order.save()

    product_ids = order.items.values_list("product_id", flat=True)
    CartItem.objects.filter(
        user=order.user,
        product_id__in=product_ids,
    ).delete()

    return True


def handle_webhook_event(payload):
    event = payload.get("event")

    if event != "payment.captured":
        return False

    payment_entity = payload["payload"]["payment"]["entity"]
    payment_id = payment_entity["id"]
    razorpay_order_id = payment_entity.get("order_id")

    if not razorpay_order_id:
        logger.warning("Webhook payment.captured missing order_id")
        return False

    from .models import Order

    try:
        order = Order.objects.get(razorpay_order_id=razorpay_order_id)
    except Order.DoesNotExist:
        logger.warning("No order found for razorpay_order_id=%s", razorpay_order_id)
        return False

    return mark_order_paid(order, payment_id)
