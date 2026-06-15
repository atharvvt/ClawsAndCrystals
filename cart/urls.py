from django.urls import path

from .views import (
    add_to_cart,
    apply_coupon_view,
    cart_view,
    decrease_quantity,
    increase_quantity,
    remove_coupon_view,
    remove_from_cart,
)

urlpatterns = [
    path("", cart_view, name="cart"),
    path("add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("remove/<str:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("increase/<str:item_id>/", increase_quantity, name="increase_quantity"),
    path("decrease/<str:item_id>/", decrease_quantity, name="decrease_quantity"),
    path("apply-coupon/", apply_coupon_view, name="apply_coupon"),
    path("remove-coupon/", remove_coupon_view, name="remove_coupon"),
]
