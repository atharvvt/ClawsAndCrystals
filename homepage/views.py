from django.contrib import messages
from django.shortcuts import render

from products.models import Product, Category

from .emails import send_contact_notification
from .forms import SuggestionForm


def home(request):
    featured_categories = Category.objects.all()[:4]

    new_arrivals = Product.objects.filter(
        status="published",
    ).order_by("-created_at")[:4]

    featured_products = Product.objects.filter(
        status="published",
        featured=True,
    )[:4]

    context = {
        "featured_categories": featured_categories,
        "new_arrivals": new_arrivals,
        "featured_products": featured_products,
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
            send_contact_notification(suggestion)
            submitted = True
            messages.success(request, "Thank you! We'll get back to you soon.")
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