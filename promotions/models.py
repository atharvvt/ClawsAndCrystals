from decimal import Decimal

from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    TYPE_PERCENT = "percent_off"
    TYPE_FIXED = "fixed_off"
    TYPE_FREE_SHIPPING = "free_shipping"

    TYPE_CHOICES = (
        (TYPE_PERCENT, "Percentage off"),
        (TYPE_FIXED, "Fixed amount off"),
        (TYPE_FREE_SHIPPING, "Free shipping"),
    )

    code = models.CharField(max_length=50, unique=True)
    coupon_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Percent or fixed rupee amount depending on type",
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    free_shipping_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("500.00"),
        help_text="Minimum subtotal for free-shipping coupons",
    )
    active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)

    def is_valid(self):
        if not self.active:
            return False

        if self.expires_at and self.expires_at < timezone.now():
            return False

        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False

        return True
