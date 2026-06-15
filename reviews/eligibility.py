from orders.models import OrderItem
from reviews.models import Review

REVIEWABLE_ORDER_STATUSES = {"delivered"}


def get_review_eligibility(user, product):
    if not user.is_authenticated:
        return "login"

    existing = Review.objects.filter(user=user, product=product).first()

    if existing:
        if existing.approved:
            return "already_reviewed"
        return "pending_approval"

    has_paid_purchase = OrderItem.objects.filter(
        order__user=user,
        order__payment_status="paid",
        product=product,
    ).exists()

    if not has_paid_purchase:
        return "not_purchased"

    has_delivered_purchase = OrderItem.objects.filter(
        order__user=user,
        order__payment_status="paid",
        order__status__in=REVIEWABLE_ORDER_STATUSES,
        product=product,
    ).exists()

    if not has_delivered_purchase:
        return "awaiting_delivery"

    return "can_review"


def can_user_review_product(user, product):
    return get_review_eligibility(user, product) == "can_review"


def get_reviewable_items_for_order(user, order):
    if order.payment_status != "paid" or order.status not in REVIEWABLE_ORDER_STATUSES:
        return []

    reviewed_product_ids = Review.objects.filter(
        user=user,
    ).values_list("product_id", flat=True)

    return list(
        order.items.select_related("product").exclude(
            product_id__in=reviewed_product_ids,
        )
    )
