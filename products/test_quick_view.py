from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from products.models import Category, Product


class QuickViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Earrings", slug="earrings")
        self.product = Product.objects.create(
            category=self.category,
            name="Crystal Earrings",
            slug="crystal-earrings",
            description="Beautiful earrings",
            price=Decimal("800.00"),
            stock=4,
            status="published",
        )

    def test_quick_view_returns_partial(self):
        response = self.client.get(reverse("quick_view", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crystal Earrings")
        self.assertContains(response, "Add To Cart")
        self.assertContains(response, "View Full Details")
