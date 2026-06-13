from cart.models import CartItem
from wishlist.models import Wishlist
from django.db.models import Sum

def navbar_counts(request):

    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:

        cart_count = (
            CartItem.objects.filter(
                user=request.user
            ).aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

    return {
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
    }