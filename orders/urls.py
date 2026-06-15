from django.urls import path

from .views import (
    checkout_view,
    my_orders_view,
    order_detail_view,
    order_success_view,
    payment_verify_view,
    payment_view,
    razorpay_webhook_view,
    retry_payment_view,
)

urlpatterns = [
    path(
        "checkout/",
        checkout_view,
        name="checkout",
    ),
    path(
        "payment/<int:order_id>/",
        payment_view,
        name="payment",
    ),
    path(
        "payment/verify/",
        payment_verify_view,
        name="payment_verify",
    ),
    path(
        "webhook/razorpay/",
        razorpay_webhook_view,
        name="razorpay_webhook",
    ),
    path(
        "payment/<int:order_id>/retry/",
        retry_payment_view,
        name="retry_payment",
    ),
    path(
        "success/<int:order_id>/",
        order_success_view,
        name="order_success",
    ),
    path(
        "my-orders/",
        my_orders_view,
        name="my_orders",
    ),
    path(
        "my-orders/<int:order_id>/",
        order_detail_view,
        name="order_detail",
    ),
]
