from django.urls import path

from .views import (
    wishlist_view,
    toggle_wishlist,
)

urlpatterns = [

    path(
        "",
        wishlist_view,
        name="wishlist"
    ),

    path(
        "toggle/<int:product_id>/",
        toggle_wishlist,
        name="toggle_wishlist"
    ),
]