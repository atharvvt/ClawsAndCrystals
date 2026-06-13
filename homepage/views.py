from django.shortcuts import render
from django.http import HttpResponse
from products.models import Product, Category

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