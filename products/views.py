from django.shortcuts import render, get_object_or_404
from wishlist.models import Wishlist

from .models import Product


def product_list(request):
    products = Product.objects.filter(
        status="published"
    )

    return render(
        request,
        "product/product_list.html",
        {
            "products": products
        }
    )


def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug,
        status="published"
    )

    related_products = Product.objects.filter(
        category=product.category,
        status="published"
    ).exclude(
        id=product.id
    )[:4]

    is_in_wishlist = False

    if request.user.is_authenticated:

        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    context = {
        "product": product,
        "related_products": related_products,
        "is_in_wishlist": is_in_wishlist,
    }

    return render(
        request,
        "product/product_detail.html",
        context,
    )