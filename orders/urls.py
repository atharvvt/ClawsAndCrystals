from django.urls import path

from .views import (
    checkout_view,
    order_success_view,
    my_orders_view,
    order_detail_view,
)
urlpatterns = [

    path(
        "checkout/",
        checkout_view,
        name="checkout"
    ),

    path(
        "success/<int:order_id>/",
        order_success_view,
        name="order_success"
    ),

    path(
    "my-orders/",
    my_orders_view,
    name="my_orders"
),

path(
    "my-orders/<int:order_id>/",
    order_detail_view,
    name="order_detail"
),
]