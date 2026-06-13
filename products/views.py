from django.shortcuts import render, get_object_or_404
from wishlist.models import Wishlist
from django.db.models import Q
from .models import Category, Product
from orders.models import OrderItem
from reviews.models import Review
from reviews.forms import ReviewForm


def product_list(request):
    products = Product.objects.filter(
        status="published"
    )

    return render(
        request,
        "product/product_list.html",
        {
            "products": products
        }
    )


def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug,
        status="published"
    )

    related_products = Product.objects.filter(
        category=product.category,
        status="published"
    ).exclude(
        id=product.id
    )[:4]

    is_in_wishlist = False

    if request.user.is_authenticated:

        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    # Reviews visible to public

    reviews = Review.objects.filter(
        product=product,
        approved=True
    )

    can_review = False
    review_form = None

    if request.user.is_authenticated:

        purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()

        already_reviewed = Review.objects.filter(
            user=request.user,
            product=product
        ).exists()

        can_review = purchased and not already_reviewed

        if can_review:

            if request.method == "POST":

                review_form = ReviewForm(
                    request.POST
                )

                if review_form.is_valid():

                    review = review_form.save(
                        commit=False
                    )

                    review.product = product
                    review.user = request.user

                    review.save()

                    review_form = ReviewForm()

            else:

                review_form = ReviewForm()

    context = {
        "product": product,
        "related_products": related_products,
        "is_in_wishlist": is_in_wishlist,
        "reviews": reviews,
        "can_review": can_review,
        "review_form": review_form,
    }

    return render(
        request,
        "product/product_detail.html",
        context,
    )

def product_list(request):

    query = request.GET.get(
        "q",
        ""
    )

    categories = Category.objects.all()

    products = Product.objects.filter(
        status="published"
    )

    if query:

        products = products.filter(
            Q(name__icontains=query) |Q(sku__icontains=query) |
            Q(category__name__icontains=query) | Q(tags__name__icontains=query)).distinct()

    context = {
        "products": products,
        "query": query,
        "categories": categories,
    }

    return render(
        request,
        "product/product_list.html",
        context,
    )