from django.contrib import admin

from .models import ShippingSettings, ShippingZone


@admin.register(ShippingSettings)
class ShippingSettingsAdmin(admin.ModelAdmin):
    list_display = ("flat_rate", "free_shipping_threshold", "is_active", "updated_at")


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "flat_rate", "free_shipping_threshold", "is_active")
    search_fields = ("name", "states", "pincode_prefixes")
