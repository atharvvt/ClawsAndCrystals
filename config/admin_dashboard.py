from decimal import Decimal

from django.db.models import Case, DecimalField, F, Sum, When
from django.utils import timezone

from orders.models import Order
from products.models import Product

LOW_STOCK_THRESHOLD = 5


def _effective_product_price():
    return Case(
        When(discounted_price__isnull=False, then=F("discounted_price")),
        default=F("price"),
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )


def get_dashboard_context():
    now = timezone.now()
    today = now.date()
    month_start = today.replace(day=1)

    paid_orders = Order.objects.filter(payment_status="paid")

    revenue_today = paid_orders.filter(paid_at__date=today).aggregate(
        total=Sum("total_amount"),
    )["total"] or Decimal("0")

    revenue_month = paid_orders.filter(paid_at__date__gte=month_start).aggregate(
        total=Sum("total_amount"),
    )["total"] or Decimal("0")

    pending_shipment = Order.objects.filter(
        payment_status="paid",
        status__in=["pending", "processing"],
    ).count()

    unpaid_orders = Order.objects.filter(
        payment_status="unpaid",
    ).exclude(status="cancelled").count()

    low_stock_products = (
        Product.objects.filter(status="published", stock__lte=LOW_STOCK_THRESHOLD)
        .annotate(effective_price=_effective_product_price())
        .order_by("stock", "name")[:10]
    )

    recent_orders = (
        Order.objects.select_related("user")
        .order_by("-created_at")[:8]
    )

    return {
        "dashboard_revenue_today": revenue_today,
        "dashboard_revenue_month": revenue_month,
        "dashboard_pending_shipment": pending_shipment,
        "dashboard_unpaid_orders": unpaid_orders,
        "dashboard_low_stock_products": low_stock_products,
        "dashboard_low_stock_threshold": LOW_STOCK_THRESHOLD,
        "dashboard_recent_orders": recent_orders,
    }
