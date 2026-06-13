from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from products.models import Product
from .models import Wishlist

@login_required
def toggle_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "product_list"
        )
    )


@login_required
def wishlist_view(request):

    items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        "product"
    )

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "items": items
        }
    )