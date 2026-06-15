from decimal import Decimal

from django.db import models


class ShippingSettings(models.Model):
    flat_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("40.00"))
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("500.00"),
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shipping settings"
        verbose_name_plural = "Shipping settings"

    def __str__(self):
        return f"Shipping (₹{self.flat_rate} below ₹{self.free_shipping_threshold})"

    @classmethod
    def get_active(cls):
        settings = cls.objects.filter(is_active=True).order_by("-updated_at").first()

        if settings:
            return settings

        return cls.objects.create()


class ShippingZone(models.Model):
    name = models.CharField(max_length=100)
    states = models.TextField(
        blank=True,
        help_text="Comma-separated state names (e.g. Maharashtra, Karnataka)",
    )
    pincode_prefixes = models.TextField(
        blank=True,
        help_text="Comma-separated pincode prefixes (e.g. 40, 41, 560)",
    )
    flat_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave blank to use global flat rate",
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave blank to use global threshold",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def state_list(self):
        return [s.strip().lower() for s in self.states.split(",") if s.strip()]

    def pincode_prefix_list(self):
        return [p.strip() for p in self.pincode_prefixes.split(",") if p.strip()]

    def matches(self, state="", pincode=""):
        state = (state or "").strip().lower()
        pincode = (pincode or "").strip()

        if self.state_list() and state in self.state_list():
            return True

        if pincode and self.pincode_prefix_list():
            for prefix in self.pincode_prefix_list():
                if pincode.startswith(prefix):
                    return True

        return False
