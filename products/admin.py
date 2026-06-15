from django.contrib import admin, messages

from config.admin_dashboard import LOW_STOCK_THRESHOLD

from .models import Category, Product, ProductImage, ProductVariant, StockNotification, Tag


admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(Tag)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "metal",
        "size",
        "stone_color",
        "sku",
        "price",
        "discounted_price",
        "stock",
        "is_default",
    )


class LowStockFilter(admin.SimpleListFilter):
    title = "stock level"
    parameter_name = "stock_level"

    def lookups(self, request, model_admin):
        return (
            ("low", f"Low stock (≤ {LOW_STOCK_THRESHOLD})"),
            ("out", "Out of stock"),
        )

    def queryset(self, request, queryset):
        if self.value() == "low":
            return queryset.filter(stock__lte=LOW_STOCK_THRESHOLD, stock__gt=0)
        if self.value() == "out":
            return queryset.filter(stock=0)
        return queryset


@admin.action(description="Mark selected as featured")
def mark_featured(modeladmin, request, queryset):
    updated = queryset.update(featured=True)
    messages.success(request, f"{updated} product(s) marked as featured.")


@admin.action(description="Remove featured flag")
def unmark_featured(modeladmin, request, queryset):
    updated = queryset.update(featured=False)
    messages.success(request, f"{updated} product(s) unfeatured.")


@admin.action(description="Publish selected products")
def publish_products(modeladmin, request, queryset):
    updated = queryset.update(status="published")
    messages.success(request, f"{updated} product(s) published.")


@admin.action(description="Unpublish selected products")
def unpublish_products(modeladmin, request, queryset):
    updated = queryset.update(status="draft", featured=False)
    messages.success(request, f"{updated} product(s) unpublished.")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "status",
        "featured",
    )

    list_filter = (
        "category",
        "status",
        "featured",
        LowStockFilter,
    )

    list_editable = ("featured", "status")

    search_fields = (
        "name",
        "sku",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    actions = [
        mark_featured,
        unmark_featured,
        publish_products,
        unpublish_products,
    ]

    inlines = [
        ProductVariantInline,
        ProductImageInline,
    ]


@admin.register(StockNotification)
class StockNotificationAdmin(admin.ModelAdmin):
    list_display = ("email", "product", "variant", "created_at", "notified_at")
    list_filter = ("notified_at",)
    search_fields = ("email", "product__name")
