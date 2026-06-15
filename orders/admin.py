from django.contrib import admin

from .models import (
    Order,
    OrderItem,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "status",
        "payment_status",
        "total_amount",
        "razorpay_order_id",
        "razorpay_payment_id",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
    )

    inlines = [
        OrderItemInline
    ]