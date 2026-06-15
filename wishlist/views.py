from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from cart.views import _resolve_variant
from products.inventory import can_increase_quantity, is_purchasable
from products.models import Product

from .models import Wishlist, WishlistShare


def _redirect_back(request):
    return redirect(request.META.get("HTTP_REFERER", "product_list"))


@login_required
def toggle_wishlist(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product,
        )

        if wishlist_item.exists():
            wishlist_item.delete()
            messages.success(request, "Removed from wishlist.")
        else:
            Wishlist.objects.create(
                user=request.user,
                product=product,
            )
            messages.success(request, "Added to wishlist.")

        return _redirect_back(request)

    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product,
    )

    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product,
        )

    return _redirect_back(request)


@login_required
@require_POST
def add_wishlist_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, status="published")
    variant = _resolve_variant(product, request.POST.get("variant"))

    if not is_purchasable(product, variant):
        messages.error(request, f"{product.name} is out of stock.")
        return redirect("wishlist")

    from cart.models import CartItem
    from cart.session_cart import add_to_session_cart

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            variant=variant,
            defaults={"quantity": 0},
        )

        if created or cart_item.quantity == 0:
            cart_item.quantity = 1
            cart_item.save()
        elif can_increase_quantity(product, cart_item.quantity, variant=variant):
            cart_item.quantity += 1
            cart_item.save()
    else:
        add_to_session_cart(
            request.session,
            product.id,
            variant.id if variant else None,
            quantity=1,
        )

    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.name} moved to cart.")
    return redirect("cart")


@login_required
@require_POST
def add_all_wishlist_to_cart(request):
    from cart.models import CartItem
    from cart.session_cart import add_to_session_cart

    items = Wishlist.objects.filter(user=request.user).select_related("product")
    added = 0

    for item in items:
        product = item.product
        variant = _resolve_variant(product, None)

        if not is_purchasable(product, variant):
            continue

        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                variant=variant,
                defaults={"quantity": 0},
            )

            if created or cart_item.quantity == 0:
                cart_item.quantity = 1
                cart_item.save()
                added += 1
            elif can_increase_quantity(product, cart_item.quantity, variant=variant):
                cart_item.quantity += 1
                cart_item.save()
                added += 1
        else:
            add_to_session_cart(
                request.session,
                product.id,
                variant.id if variant else None,
                quantity=1,
            )
            added += 1

    if added:
        messages.success(request, f"Added {added} item(s) to cart.")
    else:
        messages.warning(request, "No in-stock items to add.")

    return redirect("wishlist")


@login_required
@require_POST
def generate_wishlist_share(request):
    share, _created = WishlistShare.objects.get_or_create(user=request.user)
    share.regenerate_token()
    messages.success(request, "Share link generated.")
    return redirect("wishlist")


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(
        user=request.user,
    ).select_related("product").prefetch_related("product__images")

    share = WishlistShare.objects.filter(user=request.user, is_active=True).first()
    share_url = ""

    if share:
        share_url = request.build_absolute_uri(f"/wishlist/share/{share.token}/")

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "items": items,
            "share_url": share_url,
        },
    )


@require_GET
def shared_wishlist_view(request, token):
    share = get_object_or_404(WishlistShare, token=token, is_active=True)
    items = Wishlist.objects.filter(
        user=share.user,
    ).select_related("product").prefetch_related("product__images")

    owner_name = share.user.first_name or share.user.username

    return render(
        request,
        "wishlist/shared_wishlist.html",
        {
            "items": items,
            "owner_name": owner_name,
        },
    )
