from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .emails import send_order_status_update
from .models import Order


@receiver(pre_save, sender=Order)
def store_previous_order_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = (
                Order.objects.filter(pk=instance.pk)
                .values_list("status", flat=True)
                .first()
            )
        except Exception:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def notify_order_status_change(sender, instance, created, **kwargs):
    if created:
        return

    previous_status = getattr(instance, "_previous_status", None)

    if not previous_status or previous_status == instance.status:
        return

    send_order_status_update(instance, previous_status)
