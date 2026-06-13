from django.shortcuts import render
from django.http import HttpResponse
from products.models import Product, Category
from .forms import SuggestionForm

def home(request):

    featured_categories = Category.objects.all()[:4]

    new_arrivals = Product.objects.filter(status="published").order_by("-created_at")[:4]

    context = {
        "featured_categories": featured_categories,
        "new_arrivals": new_arrivals,
    }

    return render(
        request,
        "homepage/home.html",
        context
    )

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

            form.save()

            submitted = True

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