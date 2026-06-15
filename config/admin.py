from django.contrib import admin
from django.urls import path

from .admin_dashboard import get_dashboard_context
from .admin_reports import best_sellers_report_view, stock_value_report_view

admin.site.site_header = "Claws & Crystals"
admin.site.site_title = "C&C Admin"
admin.site.index_title = "Operations Dashboard"

_original_index = admin.site.index
_original_get_urls = admin.site.get_urls


def custom_admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context.update(get_dashboard_context())
    return _original_index(request, extra_context)


def custom_admin_get_urls():
    custom_urls = [
        path(
            "reports/stock-value/",
            admin.site.admin_view(stock_value_report_view),
            name="stock_value_report",
        ),
        path(
            "reports/best-sellers/",
            admin.site.admin_view(best_sellers_report_view),
            name="best_sellers_report",
        ),
    ]
    return custom_urls + _original_get_urls()


admin.site.index = custom_admin_index
admin.site.get_urls = custom_admin_get_urls
