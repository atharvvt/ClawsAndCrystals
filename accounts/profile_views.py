from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import CartItem
from orders.models import Order
from wishlist.models import Wishlist

from .forms import (
    ProfileForm,
    ProfileSettingsForm,
    ShippingAddressForm,
    StyledPasswordChangeForm,
)
from .models import ShippingAddress, UserProfile


def _get_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def _profile_context(user, active_section):
    return {
        "active_section": active_section,
        "order_count": Order.objects.filter(user=user).count(),
        "address_count": ShippingAddress.objects.filter(user=user).count(),
        "wishlist_count": Wishlist.objects.filter(user=user).count(),
        "cart_count": CartItem.objects.filter(user=user).count(),
    }


@login_required
def profile_dashboard(request):
    user = request.user
    profile = _get_profile(user)
    recent_orders = Order.objects.filter(user=user).order_by("-created_at")[:3]
    addresses = ShippingAddress.objects.filter(user=user)[:2]

    context = {
        **_profile_context(user, "dashboard"),
        "profile": profile,
        "recent_orders": recent_orders,
        "addresses": addresses,
    }

    return render(request, "accounts/profile/dashboard.html", context)


@login_required
def profile_edit(request):
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile_edit")
    else:
        form = ProfileForm(instance=user)

    return render(
        request,
        "accounts/profile/edit.html",
        {
            **_profile_context(user, "edit"),
            "form": form,
        },
    )


@login_required
def profile_settings(request):
    user = request.user
    profile = _get_profile(user)

    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Settings saved successfully.")
            return redirect("profile_settings")
    else:
        form = ProfileSettingsForm(instance=profile)

    return render(
        request,
        "accounts/profile/settings.html",
        {
            **_profile_context(user, "settings"),
            "form": form,
        },
    )


@login_required
def profile_password(request):
    user = request.user

    if request.method == "POST":
        form = StyledPasswordChangeForm(user, request.POST)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password updated successfully.")
            return redirect("profile_password")
    else:
        form = StyledPasswordChangeForm(user)

    return render(
        request,
        "accounts/profile/password.html",
        {
            **_profile_context(user, "password"),
            "form": form,
        },
    )


@login_required
def profile_addresses(request):
    user = request.user
    addresses = ShippingAddress.objects.filter(user=user)

    return render(
        request,
        "accounts/profile/addresses.html",
        {
            **_profile_context(user, "addresses"),
            "addresses": addresses,
        },
    )


@login_required
def profile_address_add(request):
    user = request.user

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            address.save()
            messages.success(request, "Address added successfully.")
            return redirect("profile_addresses")
    else:
        initial = {"email": user.email}

        if user.get_full_name():
            initial["full_name"] = user.get_full_name()

        form = ShippingAddressForm(initial=initial)

    return render(
        request,
        "accounts/profile/address_form.html",
        {
            **_profile_context(user, "addresses"),
            "form": form,
            "form_title": "Add Address",
        },
    )


@login_required
def profile_address_edit(request, address_id):
    user = request.user
    address = get_object_or_404(ShippingAddress, id=address_id, user=user)

    if request.method == "POST":
        form = ShippingAddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect("profile_addresses")
    else:
        form = ShippingAddressForm(instance=address)

    return render(
        request,
        "accounts/profile/address_form.html",
        {
            **_profile_context(user, "addresses"),
            "form": form,
            "form_title": "Edit Address",
            "address": address,
        },
    )


@login_required
def profile_address_delete(request, address_id):
    address = get_object_or_404(
        ShippingAddress,
        id=address_id,
        user=request.user,
    )

    if request.method == "POST":
        was_default = address.is_default
        address.delete()

        if was_default:
            next_address = ShippingAddress.objects.filter(
                user=request.user,
            ).first()

            if next_address:
                next_address.is_default = True
                next_address.save()

        messages.success(request, "Address deleted.")
        return redirect("profile_addresses")

    return render(
        request,
        "accounts/profile/address_delete.html",
        {
            **_profile_context(request.user, "addresses"),
            "address": address,
        },
    )


@login_required
def profile_address_set_default(request, address_id):
    address = get_object_or_404(
        ShippingAddress,
        id=address_id,
        user=request.user,
    )

    address.is_default = True
    address.save()
    messages.success(request, f'"{address.label}" set as default address.')
    return redirect("profile_addresses")
