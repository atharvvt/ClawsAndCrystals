from django.contrib import admin

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "coupon_type",
        "value",
        "min_order_amount",
        "active",
        "used_count",
        "usage_limit",
        "expires_at",
    )
    search_fields = ("code",)
    list_filter = ("coupon_type", "active")
