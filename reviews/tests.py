from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from orders.models import Order, OrderItem
from products.models import Category, Product
from reviews.eligibility import can_user_review_product, get_review_eligibility
from reviews.models import Review


class ReviewEligibilityTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="testpass123",
        )
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            description="Test ring",
            price=Decimal("1500.00"),
            stock=10,
            status="published",
        )

    def _create_order(self, payment_status="paid", status="delivered"):
        order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Test Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            total_amount=Decimal("1500.00"),
            payment_status=payment_status,
            status=status,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal("1500.00"),
        )
        return order

    def test_cannot_review_without_purchase(self):
        self.assertEqual(get_review_eligibility(self.user, self.product), "not_purchased")
        self.assertFalse(can_user_review_product(self.user, self.product))

    def test_cannot_review_before_delivery(self):
        self._create_order(status="processing")
        self.assertEqual(get_review_eligibility(self.user, self.product), "awaiting_delivery")

    def test_can_review_after_delivery(self):
        self._create_order()
        self.assertEqual(get_review_eligibility(self.user, self.product), "can_review")
        self.assertTrue(can_user_review_product(self.user, self.product))

    def test_cannot_review_twice(self):
        self._create_order()
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Lovely ring",
            approved=True,
        )
        self.assertEqual(get_review_eligibility(self.user, self.product), "already_reviewed")
