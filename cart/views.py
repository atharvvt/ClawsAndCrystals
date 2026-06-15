from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from products.inventory import (
    can_increase_quantity,
    is_purchasable,
    validate_cart_stock,
)
from products.models import Product

from .models import CartItem


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.status != "published":
        messages.error(request, "This product is not available.")
        return redirect(request.META.get("HTTP_REFERER", "product_list"))

    if not is_purchasable(product):
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(request.META.get("HTTP_REFERER", "product_list"))

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if created:
        cart_item.quantity = 1
        cart_item.save()
    elif can_increase_quantity(product, cart_item.quantity):
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.warning(
            request,
            f"Only {product.stock} of {product.name} available in stock.",
        )

    return redirect("cart")


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(
        user=request.user,
    ).select_related("product")

    stock_errors = validate_cart_stock(cart_items)

    total = sum(item.total_price for item in cart_items)

    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "stock_errors": stock_errors,
        },
    )


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user,
    )

    item.delete()

    return redirect("cart")


@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user,
    )

    if can_increase_quantity(item.product, item.quantity):
        item.quantity += 1
        item.save()
    else:
        messages.warning(
            request,
            f"Only {item.product.stock} of {item.product.name} available in stock.",
        )

    return redirect("cart")


@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user,
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")
