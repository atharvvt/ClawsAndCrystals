from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from products.compare import MAX_COMPARE_ITEMS, add_to_compare, get_compare_ids
from products.models import Category, Product


class CompareTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.products = [
            Product.objects.create(
                category=self.category,
                name=f"Product {index}",
                slug=f"product-{index}",
                description="Item",
                price=Decimal("100.00"),
                stock=5,
                status="published",
            )
            for index in range(1, 5)
        ]

    def test_compare_limit(self):
        session = self.client.session
        request = type("Request", (), {"session": session})()

        for product in self.products[:MAX_COMPARE_ITEMS]:
            success, _message = add_to_compare(request, product.id)
            self.assertTrue(success)

        success, message = add_to_compare(request, self.products[3].id)
        self.assertFalse(success)
        self.assertIn(str(MAX_COMPARE_ITEMS), message)
        self.assertEqual(len(get_compare_ids(request)), MAX_COMPARE_ITEMS)

    def test_compare_page_renders(self):
        for product in self.products[:2]:
            self.client.post(reverse("compare_add", args=[product.id]))

        response = self.client.get(reverse("compare_products"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product 1")
        self.assertContains(response, "Product 2")
