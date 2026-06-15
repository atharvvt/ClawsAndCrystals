MAX_RECENTLY_VIEWED = 8
SESSION_KEY = "recently_viewed"


def track_view(request, product_id):
    viewed = [pid for pid in request.session.get(SESSION_KEY, []) if pid != product_id]
    viewed.insert(0, product_id)
    request.session[SESSION_KEY] = viewed[:MAX_RECENTLY_VIEWED]
    request.session.modified = True


def get_recently_viewed_ids(request, exclude_id=None):
    ids = request.session.get(SESSION_KEY, [])

    if exclude_id:
        ids = [pid for pid in ids if pid != exclude_id]

    return ids


def get_recently_viewed_products(request, exclude_id=None, limit=4):
    from .models import Product

    ids = get_recently_viewed_ids(request, exclude_id=exclude_id)[:limit]

    if not ids:
        return []

    products = Product.objects.filter(
        pk__in=ids,
        status="published",
    ).prefetch_related("images")

    product_map = {product.id: product for product in products}
    return [product_map[pid] for pid in ids if pid in product_map]
