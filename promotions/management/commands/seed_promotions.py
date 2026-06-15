from decimal import Decimal

from django.core.management.base import BaseCommand

from promotions.models import Coupon
from shipping.models import ShippingSettings


class Command(BaseCommand):
    help = "Seed default shipping settings and promo coupons"

    def handle(self, *args, **options):
        ShippingSettings.objects.update_or_create(
            is_active=True,
            defaults={
                "flat_rate": Decimal("40.00"),
                "free_shipping_threshold": Decimal("500.00"),
            },
        )

        Coupon.objects.update_or_create(
            code="SAVE10",
            defaults={
                "coupon_type": Coupon.TYPE_PERCENT,
                "value": Decimal("10.00"),
                "min_order_amount": Decimal("0.00"),
                "active": True,
            },
        )

        Coupon.objects.update_or_create(
            code="FREESHIP",
            defaults={
                "coupon_type": Coupon.TYPE_FREE_SHIPPING,
                "value": Decimal("0.00"),
                "min_order_amount": Decimal("0.00"),
                "free_shipping_min": Decimal("500.00"),
                "active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Seeded shipping settings and coupons."))
