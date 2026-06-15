from django.contrib import messages
from django.shortcuts import render
from django.utils import timezone

from products.models import Product, Category

from .emails import send_contact_notification
from .forms import SuggestionForm
from .models import (
    Announcement,
    HomepageBanner,
    HomepageFeature,
    InstagramPost,
    Testimonial,
)


def home(request):
    featured_categories = Category.objects.all()[:4]

    new_arrivals = Product.objects.filter(
        status="published",
    ).order_by("-created_at")[:4]

    featured_products = Product.objects.filter(
        status="published",
        featured=True,
    ).prefetch_related("images")[:4]

    now = timezone.now()
    announcements = Announcement.objects.filter(is_active=True)
    active_announcements = [
        item for item in announcements if item.is_current
    ]

    context = {
        "featured_categories": featured_categories,
        "new_arrivals": new_arrivals,
        "featured_products": featured_products,
        "hero_banners": HomepageBanner.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_active=True),
        "features_list": HomepageFeature.objects.filter(is_active=True),
        "instagram_posts": InstagramPost.objects.filter(is_active=True),
        "announcements": active_announcements,
    }

    return render(request, "homepage/home.html", context)


def about(request):
    return render(
        request,
        "pages/about.html"
    )


def contact(request):

    submitted = False

    if request.method == "POST":

        form = SuggestionForm(request.POST)

        if form.is_valid():
            suggestion = form.save()
            emailed = send_contact_notification(suggestion)
            submitted = True
            if emailed:
                messages.success(request, "Thank you! We'll get back to you soon.")
            else:
                messages.success(
                    request,
                    "Thank you! Your message was saved. We'll get back to you soon.",
                )
            form = SuggestionForm()

    else:

        form = SuggestionForm()

    return render(
        request,
        "pages/contact.html",
        {
            "form": form,
            "submitted": submitted,
        }
    )
