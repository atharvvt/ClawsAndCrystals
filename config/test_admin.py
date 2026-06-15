from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from config.admin_dashboard import get_dashboard_context
from config.admin_reports import get_best_sellers, get_stock_value_report
from homepage.models import Suggestion
from orders.models import Order, OrderItem
from products.models import Category, Product
from reviews.models import Review


class DashboardStatsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            description="Ring",
            price=Decimal("1000.00"),
            stock=3,
            status="published",
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Street",
            city="Mumbai",
            state="MH",
            pincode="400001",
            subtotal_amount=Decimal("1000.00"),
            total_amount=Decimal("1000.00"),
            status="processing",
            payment_status="paid",
            paid_at=timezone.now(),
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal("1000.00"),
        )

    def test_dashboard_context_metrics(self):
        context = get_dashboard_context()

        self.assertEqual(context["dashboard_revenue_today"], Decimal("1000.00"))
        self.assertEqual(context["dashboard_pending_shipment"], 1)
        self.assertEqual(len(context["dashboard_low_stock_products"]), 1)

    def test_admin_index_shows_dashboard(self):
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revenue today")
        self.assertContains(response, "Pending shipment")
        self.assertContains(response, "Gold Ring")


class InventoryReportsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.category = Category.objects.create(name="Necklaces", slug="necklaces")
        self.product = Product.objects.create(
            category=self.category,
            name="Pearl Necklace",
            slug="pearl-necklace",
            description="Necklace",
            price=Decimal("500.00"),
            stock=4,
            status="published",
        )

    def test_stock_value_report(self):
        report = get_stock_value_report()
        self.assertEqual(report["product_total"], Decimal("2000.00"))
        self.assertEqual(report["grand_total"], Decimal("2000.00"))

    def test_stock_value_admin_page(self):
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("admin:stock_value_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pearl Necklace")

    def test_best_sellers_report(self):
        order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Street",
            city="Mumbai",
            state="MH",
            pincode="400001",
            subtotal_amount=Decimal("1000.00"),
            total_amount=Decimal("1000.00"),
            payment_status="paid",
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal("500.00"),
        )

        sellers = list(get_best_sellers())
        self.assertEqual(len(sellers), 1)
        self.assertEqual(sellers[0]["units_sold"], 2)

    def test_best_sellers_admin_page(self):
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("admin:best_sellers_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Best Sellers")


@override_settings(
    ADMIN_ORDER_EMAIL="admin@example.com",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ContactNotificationTest(TestCase):
    def test_contact_form_emails_admin(self):
        mail.outbox.clear()
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Priya",
                "email": "priya@example.com",
                "subject": "Wholesale enquiry",
                "message": "Interested in bulk order.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Wholesale enquiry", mail.outbox[0].subject)
        self.assertIn("admin@example.com", mail.outbox[0].to)
        self.assertEqual(Suggestion.objects.count(), 1)


class AdminBulkActionsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.buyer = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="buyerpass123",
        )
        self.category = Category.objects.create(name="Earrings", slug="earrings")
        self.product = Product.objects.create(
            category=self.category,
            name="Crystal Earrings",
            slug="crystal-earrings",
            description="Earrings",
            price=Decimal("800.00"),
            stock=10,
            status="published",
            featured=False,
        )
        self.order = Order.objects.create(
            user=self.buyer,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9999999999",
            address="123 Street",
            city="Mumbai",
            state="MH",
            pincode="400001",
            subtotal_amount=Decimal("800.00"),
            total_amount=Decimal("800.00"),
            payment_status="paid",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal("800.00"),
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.buyer,
            rating=5,
            comment="Lovely!",
            approved=False,
        )
        self.client.login(username="admin", password="adminpass123")

    def test_mark_featured_action(self):
        url = reverse("admin:products_product_changelist")
        response = self.client.post(
            url,
            {
                "action": "mark_featured",
                "_selected_action": [self.product.id],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertTrue(self.product.featured)

    def test_unpublish_action(self):
        url = reverse("admin:products_product_changelist")
        response = self.client.post(
            url,
            {
                "action": "unpublish_products",
                "_selected_action": [self.product.id],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, "draft")
        self.assertFalse(self.product.featured)

    def test_export_orders_csv(self):
        url = reverse("admin:orders_order_changelist")
        response = self.client.post(
            url,
            {
                "action": "export_orders_csv",
                "_selected_action": [self.order.id],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(b"Crystal Earrings", response.content)

    def test_approve_reviews_action(self):
        url = reverse("admin:reviews_review_changelist")
        response = self.client.post(
            url,
            {
                "action": "approve_reviews",
                "_selected_action": [self.review.id],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.review.refresh_from_db()
        self.assertTrue(self.review.approved)
