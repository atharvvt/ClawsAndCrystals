from django.conf import settings
from django.utils import timezone

from config.emails import send_templated_email

from .models import StockNotification


def send_back_in_stock_notifications(product, variant=None):
    pending = StockNotification.objects.filter(
        product=product,
        variant=variant,
        notified_at__isnull=True,
    )

    if not pending.exists():
        return 0

    variant_label = variant.display_label if variant else ""
    product_url = f"{settings.SITE_URL}/products/{product.slug}/"
    if variant:
        product_url = f"{product_url}?variant={variant.id}"

    sent_count = 0

    for notification in pending:
        context = {
            "product": product,
            "variant": variant,
            "variant_label": variant_label,
            "product_url": product_url,
        }

        if send_templated_email(
            subject=f"Back in stock: {product.name}",
            template_name="back_in_stock",
            context=context,
            recipient_list=[notification.email],
        ):
            notification.notified_at = timezone.now()
            notification.save(update_fields=["notified_at"])
            sent_count += 1

    return sent_count
