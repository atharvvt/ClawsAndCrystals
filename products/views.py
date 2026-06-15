from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Case, DecimalField, F, Q, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from reviews.eligibility import get_review_eligibility
from reviews.models import Review
from wishlist.models import Wishlist

from .compare import (
    MAX_COMPARE_ITEMS,
    add_to_compare,
    get_compare_ids,
    get_compare_products,
    remove_from_compare,
)
from .models import Category, Product, ProductVariant, StockNotification, Tag
from .recently_viewed import get_recently_viewed_products, track_view
from .search_utils import get_did_you_mean, get_search_suggestions

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
    query = request.GET.get("q", "").strip()
    did_you_mean = ""

    if query and not page_obj.object_list:
        did_you_mean = get_did_you_mean(query)

    return {
        "products": page_obj,
        "page_obj": page_obj,
        "category": category,
        "categories": Category.objects.all(),
        "query": query,
        "result_count": paginator.count,
        "did_you_mean": did_you_mean,
        "sort": request.GET.get("sort", "newest"),
        "material": request.GET.get("material", "").strip(),
        "tag": request.GET.get("tag", "").strip(),
        "min_price": request.GET.get("min_price", "").strip(),
        "max_price": request.GET.get("max_price", "").strip(),
        "materials": materials,
        "tags": tags,
        "recently_viewed": get_recently_viewed_products(request, limit=4),
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


def _product_detail_context(request, product):
    related_products = Product.objects.filter(
        category=product.category,
        status="published",
    ).exclude(
        id=product.id,
    ).prefetch_related("images")[:4]

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

    review_eligibility = "login"
    open_review_modal = request.GET.get("review") == "1"

    if request.user.is_authenticated:
        review_eligibility = get_review_eligibility(request.user, product)

    variants = list(product.variants.all())
    selected_variant = None

    if variants:
        variant_id = request.GET.get("variant")
        if variant_id:
            selected_variant = next(
                (v for v in variants if str(v.id) == str(variant_id)),
                None,
            )
        if selected_variant is None:
            selected_variant = next(
                (v for v in variants if v.is_default),
                variants[0],
            )

    display_stock = selected_variant.stock if selected_variant else product.stock
    display_price = (
        selected_variant.effective_price
        if selected_variant
        else (product.discounted_price or product.price)
    )
    display_sku = selected_variant.sku if selected_variant and selected_variant.sku else product.sku
    is_in_stock = display_stock > 0

    variant_options = {
        "metals": sorted({v.metal for v in variants if v.metal}),
        "sizes": sorted({v.size for v in variants if v.size}),
        "stone_colors": sorted({v.stone_color for v in variants if v.stone_color}),
    }

    variants_json = [
        {
            "id": variant.id,
            "metal": variant.metal,
            "size": variant.size,
            "stone_color": variant.stone_color,
            "sku": variant.sku or "",
            "price": str(variant.effective_price),
            "stock": variant.stock,
        }
        for variant in variants
    ]

    compare_ids = get_compare_ids(request)
    share_url = request.build_absolute_uri()
    share_text = f"Check out {product.name} at Claws & Crystals"
    whatsapp_url = (
        "https://wa.me/?text="
        + f"{share_text} {share_url}".replace(" ", "%20")
    )

    primary_image = product.primary_image
    og_image_url = ""
    if primary_image:
        og_image_url = request.build_absolute_uri(primary_image.image.url)

    return {
        "product": product,
        "related_products": related_products,
        "is_in_wishlist": is_in_wishlist,
        "reviews": reviews,
        "can_review": review_eligibility == "can_review",
        "review_eligibility": review_eligibility,
        "open_review_modal": open_review_modal and review_eligibility == "can_review",
        "variants": variants,
        "variants_json": variants_json,
        "selected_variant": selected_variant,
        "variant_options": variant_options,
        "display_stock": display_stock,
        "display_price": display_price,
        "display_sku": display_sku,
        "is_in_stock": is_in_stock,
        "notify_email": request.user.email if request.user.is_authenticated else "",
        "recently_viewed": get_recently_viewed_products(request, exclude_id=product.id, limit=4),
        "in_compare": product.id in compare_ids,
        "compare_full": len(compare_ids) >= MAX_COMPARE_ITEMS,
        "share_url": share_url,
        "whatsapp_url": whatsapp_url,
        "og_image_url": og_image_url,
    }


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("images", "variants", "tags"),
        slug=slug,
        status="published",
    )

    track_view(request, product.id)

    context = _product_detail_context(request, product)

    return render(
        request,
        "product/product_detail.html",
        context,
    )


def quick_view(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("images", "variants"),
        slug=slug,
        status="published",
    )

    context = _product_detail_context(request, product)

    return render(
        request,
        "product/quick_view_modal.html",
        context,
    )


@require_GET
def search_suggest(request):
    query = request.GET.get("q", "").strip()
    suggestions = get_search_suggestions(query)
    return JsonResponse(suggestions, safe=False)


@require_POST
def compare_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status="published")
    success, message = add_to_compare(request, product.id)

    if success:
        messages.success(request, message)
    else:
        messages.warning(request, message)

    return redirect(request.META.get("HTTP_REFERER", "product_list"))


@require_POST
def compare_remove(request, product_id):
    remove_from_compare(request, product_id)
    messages.success(request, "Removed from compare.")
    return redirect(request.META.get("HTTP_REFERER", "compare_products"))


def compare_view(request):
    products = get_compare_products(request)

    return render(
        request,
        "product/compare.html",
        {
            "products": products,
            "compare_ids": get_compare_ids(request),
        },
    )


@require_POST
def notify_stock_view(request, slug):
    product = get_object_or_404(Product, slug=slug, status="published")
    email = request.POST.get("email", "").strip()
    variant_id = request.POST.get("variant_id")

    if not email:
        messages.error(request, "Please enter your email address.")
        return redirect("product_detail", slug=slug)

    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(pk=variant_id, product=product).first()

    StockNotification.objects.get_or_create(
        product=product,
        variant=variant,
        email=email,
        defaults={"user": request.user if request.user.is_authenticated else None},
    )

    messages.success(request, "We'll email you when this item is back in stock.")
    return redirect("product_detail", slug=slug)
