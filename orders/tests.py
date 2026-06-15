from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import UserProfile
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


@override_settings(
    ADMIN_ORDER_EMAIL="admin@example.com",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class OrderEmailTest(TestCase):

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

    def test_mark_order_paid_sends_confirmation_and_admin_emails(self):
        mail.outbox.clear()

        mark_order_paid(self.order, "pay_test123")

        self.assertEqual(len(mail.outbox), 2)
        recipients = {addr for msg in mail.outbox for addr in msg.to}
        self.assertIn("buyer@example.com", recipients)
        self.assertIn("admin@example.com", recipients)

    def test_mark_order_paid_skips_customer_email_when_opted_out(self):
        UserProfile.objects.filter(user=self.user).update(
            receive_order_updates=False
        )
        mail.outbox.clear()

        mark_order_paid(self.order, "pay_test123")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["admin@example.com"])

    def test_status_change_sends_email_when_shipped(self):
        self.order.payment_status = "paid"
        self.order.status = "processing"
        self.order.save()
        mail.outbox.clear()

        self.order.status = "shipped"
        self.order.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["buyer@example.com"])
        self.assertIn("shipped", mail.outbox[0].subject.lower())

    def test_processing_status_does_not_send_status_email(self):
        self.order.payment_status = "paid"
        self.order.status = "pending"
        self.order.save()
        mail.outbox.clear()

        self.order.status = "processing"
        self.order.save()

        self.assertEqual(len(mail.outbox), 0)


class CancelUnpaidOrdersTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="testpass123",
        )

    def test_cancels_stale_unpaid_orders(self):
        stale = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Test Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            total_amount=Decimal("1500.00"),
            payment_status="unpaid",
        )
        Order.objects.filter(pk=stale.pk).update(
            created_at=timezone.now() - timedelta(hours=72),
        )
        recent = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Test Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            total_amount=Decimal("1500.00"),
            payment_status="unpaid",
        )

        call_command("cancel_unpaid_orders")

        stale.refresh_from_db()
        recent.refresh_from_db()
        self.assertEqual(stale.status, "cancelled")
        self.assertNotEqual(recent.status, "cancelled")
