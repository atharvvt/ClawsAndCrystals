from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Case, DecimalField, F, Q, When
from django.shortcuts import get_object_or_404, render

from orders.models import OrderItem
from reviews.forms import ReviewForm
from reviews.models import Review
from wishlist.models import Wishlist

from .models import Category, Product, Tag

PRODUCTS_PER_PAGE = 12


def _effective_price_annotation():
    return Case(
        When(discounted_price__isnull=False, then=F("discounted_price")),
        default=F("price"),
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )


def get_filter_options():
    published = Product.objects.filter(status="published")

    materials = (
        published.exclude(material="")
        .values_list("material", flat=True)
        .distinct()
        .order_by("material")
    )

    tags = Tag.objects.filter(
        product__status="published",
    ).distinct().order_by("name")

    return materials, tags


def get_filtered_products(request, category=None):
    products = Product.objects.filter(
        status="published",
    ).select_related("category").prefetch_related("images", "tags")

    if category:
        products = products.filter(category=category)

    query = request.GET.get("q", "").strip()

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()

    material = request.GET.get("material", "").strip()

    if material:
        products = products.filter(material=material)

    tag = request.GET.get("tag", "").strip()

    if tag:
        products = products.filter(tags__name=tag)

    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    products = products.annotate(
        effective_price=_effective_price_annotation(),
    )

    if min_price:
        try:
            products = products.filter(
                effective_price__gte=Decimal(min_price),
            )
        except (InvalidOperation, ValueError):
            pass

    if max_price:
        try:
            products = products.filter(
                effective_price__lte=Decimal(max_price),
            )
        except (InvalidOperation, ValueError):
            pass

    sort = request.GET.get("sort", "newest")

    if sort == "price_asc":
        products = products.order_by("effective_price", "name")
    elif sort == "price_desc":
        products = products.order_by("-effective_price", "name")
    else:
        products = products.order_by("-created_at")

    return products


def _product_list_context(request, category=None):
    products = get_filtered_products(request, category=category)
    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    materials, tags = get_filter_options()

    return {
        "products": page_obj,
        "page_obj": page_obj,
        "category": category,
        "categories": Category.objects.all(),
        "query": request.GET.get("q", "").strip(),
        "sort": request.GET.get("sort", "newest"),
        "material": request.GET.get("material", "").strip(),
        "tag": request.GET.get("tag", "").strip(),
        "min_price": request.GET.get("min_price", "").strip(),
        "max_price": request.GET.get("max_price", "").strip(),
        "materials": materials,
        "tags": tags,
    }


def product_list(request):
    context = _product_list_context(request)

    return render(
        request,
        "product/product_list.html",
        context,
    )


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    context = _product_list_context(request, category=category)

    return render(
        request,
        "product/product_list.html",
        context,
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        status="published",
    )

    related_products = Product.objects.filter(
        category=product.category,
        status="published",
    ).exclude(
        id=product.id,
    )[:4]

    is_in_wishlist = False

    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product,
        ).exists()

    reviews = Review.objects.filter(
        product=product,
        approved=True,
    )

    can_review = False
    review_form = None

    if request.user.is_authenticated:
        purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
        ).exists()

        already_reviewed = Review.objects.filter(
            user=request.user,
            product=product,
        ).exists()

        can_review = purchased and not already_reviewed

        if can_review:
            if request.method == "POST":
                review_form = ReviewForm(request.POST)

                if review_form.is_valid():
                    review = review_form.save(commit=False)
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
