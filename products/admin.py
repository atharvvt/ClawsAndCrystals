from django.contrib import admin
from .models import Category, Product, ProductImage, Tag


admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(Tag)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "status",
        "featured"
    )

    list_filter = (
        "category",
        "status",
        "featured"
    )

    search_fields = (
        "name",
        "sku"
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    inlines = [
        ProductImageInline
    ]
