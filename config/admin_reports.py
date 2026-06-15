from decimal import Decimal

from django.db.models import Case, Count, DecimalField, F, Sum, When
from django.template.response import TemplateResponse

from orders.models import OrderItem
from products.models import Product, ProductVariant


def _effective_product_price():
    return Case(
        When(discounted_price__isnull=False, then=F("discounted_price")),
        default=F("price"),
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )


def _effective_variant_price():
    return Case(
        When(discounted_price__isnull=False, then=F("discounted_price")),
        When(price__isnull=False, then=F("price")),
        default=F("product__price"),
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )


def get_stock_value_report():
    product_rows = (
        Product.objects.exclude(status="draft")
        .annotate(unit_price=_effective_product_price())
        .annotate(line_value=F("unit_price") * F("stock"))
        .order_by("-line_value")
    )

    variant_rows = (
        ProductVariant.objects.select_related("product")
        .annotate(unit_price=_effective_variant_price())
        .annotate(line_value=F("unit_price") * F("stock"))
        .filter(stock__gt=0)
        .order_by("-line_value")
    )

    product_total = sum((row.line_value for row in product_rows), Decimal("0"))
    variant_total = sum((row.line_value for row in variant_rows), Decimal("0"))

    return {
        "product_rows": product_rows,
        "variant_rows": variant_rows,
        "product_total": product_total,
        "variant_total": variant_total,
        "grand_total": product_total + variant_total,
    }


def get_best_sellers(limit=20):
    return (
        OrderItem.objects.filter(order__payment_status="paid")
        .values("product_id", "product__name", "product__slug")
        .annotate(
            units_sold=Sum("quantity"),
            revenue=Sum(F("price") * F("quantity"), output_field=DecimalField()),
            order_count=Count("order", distinct=True),
        )
        .order_by("-units_sold")[:limit]
    )


def stock_value_report_view(request):
    context = {
        **get_stock_value_report(),
        **admin_site_context(request),
        "title": "Stock Value Report",
    }
    return TemplateResponse(request, "admin/reports/stock_value.html", context)


def best_sellers_report_view(request):
    context = {
        "best_sellers": get_best_sellers(),
        **admin_site_context(request),
        "title": "Best Sellers",
    }
    return TemplateResponse(request, "admin/reports/best_sellers.html", context)


def admin_site_context(request):
    from django.contrib import admin

    return admin.site.each_context(request)
