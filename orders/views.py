from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import (
    render,
    redirect,
)

from cart.models import CartItem

from .models import (
    Order,
    OrderItem,
)


@login_required
def checkout_view(request):

    cart_items = CartItem.objects.filter(
        user=request.user
    ).select_related("product")

    if not cart_items.exists():
        return redirect("cart")

    total = sum(
        item.total_price
        for item in cart_items
    )

    if request.method == "POST":

        order = Order.objects.create(
            user=request.user,

            full_name=request.POST["full_name"],
            email=request.POST["email"],
            phone=request.POST["phone"],

            address=request.POST["address"],
            city=request.POST["city"],
            state=request.POST["state"],
            pincode=request.POST["pincode"],

            total_amount=total,
        )

        for item in cart_items:

            price = (
                item.product.discounted_price
                or item.product.price
            )

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=price,
            )

        cart_items.delete()

        return redirect(
            "order_success",
            order_id=order.id
        )

    return render(
        request,
        "orders/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


@login_required
def order_success_view(
    request,
    order_id
):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/success.html",
        {
            "order": order
        }
    )

@login_required
def my_orders_view(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "orders/my_orders.html",
        {
            "orders": orders
        }
    )


@login_required
def order_detail_view(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order
        }
    )