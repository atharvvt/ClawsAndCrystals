from django.contrib import admin, messages

from .models import (
    Announcement,
    HomepageBanner,
    HomepageFeature,
    InstagramPost,
    Suggestion,
    Testimonial,
)


@admin.action(description="Mark selected as reviewed")
def mark_reviewed(modeladmin, request, queryset):
    updated = queryset.update(reviewed=True)
    messages.success(request, f"{updated} message(s) marked as reviewed.")


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "reviewed", "created_at")
    list_filter = ("reviewed", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    actions = [mark_reviewed]
    ordering = ("-created_at",)


@admin.register(HomepageBanner)
class HomepageBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "rating", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("message", "is_active", "starts_at", "ends_at")


@admin.register(HomepageFeature)
class HomepageFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "sort_order", "link_url")
    list_editable = ("is_active", "sort_order")
