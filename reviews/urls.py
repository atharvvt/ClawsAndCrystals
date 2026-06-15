from django.urls import path

from . import views

urlpatterns = [
    path(
        "submit/<slug:product_slug>/",
        views.submit_review,
        name="submit_review",
    ),
]
