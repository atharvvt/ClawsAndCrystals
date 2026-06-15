import difflib

from django.db.models import Q

from .models import Category, Product


def get_search_suggestions(query, limit=8):
    query = (query or "").strip()

    if len(query) < 2:
        return []

    products = (
        Product.objects.filter(status="published")
        .filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query)
        )
        .distinct()
        .select_related("category")
        .prefetch_related("images")[:limit]
    )

    suggestions = []

    for product in products:
        image_url = ""
        if product.primary_image:
            image_url = product.primary_image.image.url

        suggestions.append(
            {
                "name": product.name,
                "slug": product.slug,
                "price": str(product.discounted_price or product.price),
                "image_url": image_url,
            }
        )

    return suggestions


def get_did_you_mean(query):
    query = (query or "").strip().lower()

    if len(query) < 3:
        return ""

    product_names = list(
        Product.objects.filter(status="published").values_list("name", flat=True)
    )
    category_names = list(Category.objects.values_list("name", flat=True))
    choices = [name.lower() for name in product_names + category_names]

    matches = difflib.get_close_matches(query, choices, n=1, cutoff=0.6)
    return matches[0] if matches else ""
