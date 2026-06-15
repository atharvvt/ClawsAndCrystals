from django.urls import path

from .views import (
    add_all_wishlist_to_cart,
    add_wishlist_to_cart,
    generate_wishlist_share,
    shared_wishlist_view,
    toggle_wishlist,
    wishlist_view,
)

urlpatterns = [
    path("", wishlist_view, name="wishlist"),
    path("toggle/<int:product_id>/", toggle_wishlist, name="toggle_wishlist"),
    path("add-to-cart/<int:product_id>/", add_wishlist_to_cart, name="wishlist_add_to_cart"),
    path("add-all-to-cart/", add_all_wishlist_to_cart, name="wishlist_add_all_to_cart"),
    path("share/generate/", generate_wishlist_share, name="wishlist_share_generate"),
    path("share/<uuid:token>/", shared_wishlist_view, name="wishlist_share"),
]
