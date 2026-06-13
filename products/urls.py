from django.urls import path

from products.models import category_products
from . import views

urlpatterns = [
    path( "",views.product_list,name="product_list"),
    path("category/<slug:slug>/",category_products,name="category_products"),
    path( "<slug:slug>/", views.product_detail,name="product_detail"),
]