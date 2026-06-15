from django.urls import path

from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("suggest/", views.search_suggest, name="search_suggest"),
    path("compare/", views.compare_view, name="compare_products"),
    path("compare/add/<int:product_id>/", views.compare_add, name="compare_add"),
    path("compare/remove/<int:product_id>/", views.compare_remove, name="compare_remove"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    path("<slug:slug>/quick-view/", views.quick_view, name="quick_view"),
    path("<slug:slug>/notify-stock/", views.notify_stock_view, name="notify_stock"),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
]
