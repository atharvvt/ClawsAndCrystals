from django.contrib import admin, messages

from .models import Review


@admin.action(description="Approve selected reviews")
def approve_reviews(modeladmin, request, queryset):
    updated = queryset.update(approved=True)
    messages.success(request, f"{updated} review(s) approved.")


@admin.action(description="Reject selected reviews")
def reject_reviews(modeladmin, request, queryset):
    updated = queryset.update(approved=False)
    messages.success(request, f"{updated} review(s) rejected.")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "user",
        "rating",
        "approved",
        "created_at",
    )

    list_filter = (
        "approved",
        "rating",
        "created_at",
    )

    list_editable = ("approved",)

    search_fields = (
        "product__name",
        "user__username",
        "comment",
    )

    readonly_fields = ("product", "user", "created_at")
    actions = [approve_reviews, reject_reviews]
    ordering = ("-created_at",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ("created_at",)
