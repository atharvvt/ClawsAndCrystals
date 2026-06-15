from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from products.models import Product

from .eligibility import can_user_review_product
from .forms import ReviewForm


@login_required
@require_POST
def submit_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, status="published")

    if not can_user_review_product(request.user, product):
        messages.error(
            request,
            "You can only review products from delivered orders you have purchased.",
        )
        return redirect(request.POST.get("next") or reverse("product_detail", args=[product.slug]))

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(
            request,
            "Thank you! Your review has been submitted and will appear after approval.",
        )
    else:
        messages.error(request, "Please select a rating and write your review.")

    return redirect(request.POST.get("next") or reverse("product_detail", args=[product.slug]))
