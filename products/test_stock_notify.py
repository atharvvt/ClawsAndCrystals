from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings

from products.inventory import restore_stock_for_order
from products.models import Category, Product, ProductVariant, StockNotification
from products.stock_notify import send_back_in_stock_notifications
from orders.models import Order, OrderItem


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class StockNotificationTest(TestCase):

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
            stock=0,
            status="out_of_stock",
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            stock=0,
            is_default=True,
        )
        StockNotification.objects.create(
            product=self.product,
            variant=self.variant,
            email="notify@example.com",
        )

    def test_back_in_stock_email_sent(self):
        self.variant.stock = 3
        self.variant.save()

        sent = send_back_in_stock_notifications(self.product, self.variant)

        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("back in stock", mail.outbox[0].subject.lower())

    def test_restore_stock_triggers_notification(self):
        order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Test Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            subtotal_amount=Decimal("1500.00"),
            total_amount=Decimal("1500.00"),
            payment_status="paid",
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            variant=self.variant,
            quantity=1,
            price=Decimal("1500.00"),
        )
        self.variant.stock = 0
        self.variant.save()

        restore_stock_for_order(order)

        self.assertEqual(len(mail.outbox), 1)
