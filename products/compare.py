MAX_COMPARE_ITEMS = 3
SESSION_KEY = "compare_list"


def get_compare_ids(request):
    ids = request.session.get(SESSION_KEY, [])
    return [pid for pid in ids if isinstance(pid, int)][:MAX_COMPARE_ITEMS]


def add_to_compare(request, product_id):
    compare_ids = get_compare_ids(request)

    if product_id in compare_ids:
        return True, "Already in compare list."

    if len(compare_ids) >= MAX_COMPARE_ITEMS:
        return False, f"You can compare up to {MAX_COMPARE_ITEMS} products."

    compare_ids.append(product_id)
    request.session[SESSION_KEY] = compare_ids
    request.session.modified = True
    return True, "Added to compare."


def remove_from_compare(request, product_id):
    compare_ids = [pid for pid in get_compare_ids(request) if pid != product_id]
    request.session[SESSION_KEY] = compare_ids
    request.session.modified = True


def clear_compare(request):
    request.session.pop(SESSION_KEY, None)
    request.session.modified = True


def get_compare_products(request):
    from .models import Product

    ids = get_compare_ids(request)

    if not ids:
        return []

    products = Product.objects.filter(
        pk__in=ids,
        status="published",
    ).prefetch_related("images", "variants")

    product_map = {product.id: product for product in products}
    return [product_map[pid] for pid in ids if pid in product_map]
