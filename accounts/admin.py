from django.contrib import admin

from .models import ShippingAddress, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "receive_order_updates", "receive_promotions", "updated_at")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "label",
        "full_name",
        "city",
        "is_default",
        "created_at",
    )
    list_filter = ("is_default",)
    search_fields = ("user__username", "full_name", "city")
