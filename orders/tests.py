from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from cart.models import CartItem
from orders.models import Order, OrderItem
from orders.payments import (
    RazorpayConfigError,
    amount_in_paise,
    handle_webhook_event,
    mark_order_paid,
    validate_razorpay_config,
)
from products.models import Category, Product


class PaymentHelpersTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="testpass123",
        )
        self.category = Category.objects.create(
            name="Rings",
            slug="rings",
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            description="Test ring",
            price=Decimal("1500.00"),
            stock=10,
            status="published",
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Test Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            total_amount=Decimal("1500.00"),
            razorpay_order_id="order_test123",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal("1500.00"),
        )
        CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1,
        )

    def test_validate_razorpay_config_requires_keys(self):
        with self.settings(RAZORPAY_KEY_ID="", RAZORPAY_KEY_SECRET=""):
            with self.assertRaises(RazorpayConfigError):
                validate_razorpay_config()

    def test_amount_in_paise(self):
        self.assertEqual(amount_in_paise(Decimal("99.50")), 9950)

    def test_mark_order_paid_clears_cart(self):
        result = mark_order_paid(self.order, "pay_test123", "sig_test")

        self.assertTrue(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "processing")
        self.assertEqual(self.order.razorpay_payment_id, "pay_test123")
        self.assertIsNotNone(self.order.paid_at)
        self.assertFalse(
            CartItem.objects.filter(user=self.user, product=self.product).exists()
        )

    def test_mark_order_paid_is_idempotent(self):
        mark_order_paid(self.order, "pay_test123")
        self.order.refresh_from_db()
        paid_at = self.order.paid_at

        result = mark_order_paid(self.order, "pay_test456")

        self.assertFalse(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.razorpay_payment_id, "pay_test123")
        self.assertEqual(self.order.paid_at, paid_at)

    def test_handle_webhook_event_marks_order_paid(self):
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_webhook123",
                        "order_id": "order_test123",
                    }
                }
            },
        }

        result = handle_webhook_event(payload)

        self.assertTrue(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.razorpay_payment_id, "pay_webhook123")

    def test_handle_webhook_event_ignores_other_events(self):
        payload = {"event": "payment.failed", "payload": {}}

        result = handle_webhook_event(payload)

        self.assertFalse(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, "unpaid")
