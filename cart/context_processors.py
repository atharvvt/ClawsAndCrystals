from cart.utils import get_cart_count
from wishlist.models import Wishlist


def navbar_counts(request):
    wishlist_count = 0

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        "cart_count": get_cart_count(request),
        "wishlist_count": wishlist_count,
    }
