import csv

from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils import timezone

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "variant", "variant_label", "quantity", "price")
    can_delete = False


@admin.action(description="Export selected orders to CSV")
def export_orders_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    filename = f"orders-{timezone.now().strftime('%Y%m%d')}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        "order_id",
        "created_at",
        "customer_name",
        "email",
        "phone",
        "status",
        "payment_status",
        "subtotal",
        "discount",
        "shipping",
        "total",
        "coupon_code",
        "razorpay_order_id",
        "razorpay_payment_id",
        "paid_at",
        "city",
        "state",
        "pincode",
        "address",
        "product",
        "variant",
        "quantity",
        "item_price",
    ])

    orders = queryset.select_related("user").prefetch_related("items__product", "items__variant")

    for order in orders:
        items = list(order.items.all())
        rows = items or [None]

        for item in rows:
            writer.writerow([
                order.id,
                order.created_at.isoformat(),
                order.full_name,
                order.email,
                order.phone,
                order.status,
                order.payment_status,
                order.subtotal_amount,
                order.discount_amount,
                order.shipping_amount,
                order.total_amount,
                order.coupon_code,
                order.razorpay_order_id or "",
                order.razorpay_payment_id or "",
                order.paid_at.isoformat() if order.paid_at else "",
                order.city,
                order.state,
                order.pincode,
                order.address,
                item.product.name if item else "",
                item.variant_label if item else "",
                item.quantity if item else "",
                item.price if item else "",
            ])

    return response


@admin.action(description="Mark as processing")
def mark_processing(modeladmin, request, queryset):
    updated = queryset.exclude(status="cancelled").update(status="processing")
    messages.success(request, f"{updated} order(s) marked as processing.")


@admin.action(description="Mark as shipped")
def mark_shipped(modeladmin, request, queryset):
    updated = queryset.filter(payment_status="paid").exclude(status="cancelled").update(status="shipped")
    messages.success(request, f"{updated} order(s) marked as shipped.")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
        "paid_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "id",
        "full_name",
        "email",
        "phone",
        "razorpay_order_id",
        "razorpay_payment_id",
        "user__username",
    )

    readonly_fields = (
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
        "paid_at",
        "created_at",
        "subtotal_amount",
        "discount_amount",
        "shipping_amount",
        "total_amount",
        "coupon_code",
        "applied_coupon",
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    actions = [export_orders_csv, mark_processing, mark_shipped]

    fieldsets = (
        ("Customer", {
            "fields": ("user", "full_name", "email", "phone"),
        }),
        ("Shipping", {
            "fields": ("address", "city", "state", "pincode"),
        }),
        ("Totals", {
            "fields": (
                "subtotal_amount",
                "discount_amount",
                "shipping_amount",
                "total_amount",
                "coupon_code",
                "applied_coupon",
            ),
        }),
        ("Status", {
            "fields": ("status", "payment_status", "paid_at", "created_at"),
        }),
        ("Razorpay", {
            "fields": ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature"),
            "classes": ("collapse",),
        }),
    )

    inlines = [OrderItemInline]
