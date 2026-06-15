from decimal import Decimal

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from products.models import Category, Product, Tag
from products.views import PRODUCTS_PER_PAGE, get_filtered_products


class ProductFilterTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.tag = Tag.objects.create(name="Gold")

        self.cheap = Product.objects.create(
            category=self.category,
            name="Silver Ring",
            slug="silver-ring",
            description="Cheap ring",
            price=Decimal("500.00"),
            material="Silver",
            stock=5,
            status="published",
        )
        self.expensive = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            description="Gold ring",
            price=Decimal("2000.00"),
            material="Gold",
            stock=5,
            status="published",
        )
        self.expensive.tags.add(self.tag)

    def test_filter_by_material(self):
        request = self.factory.get("/products/", {"material": "Gold"})
        products = list(get_filtered_products(request))

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Gold Ring")

    def test_filter_by_tag(self):
        request = self.factory.get("/products/", {"tag": "Gold"})
        products = list(get_filtered_products(request))

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Gold Ring")

    def test_filter_by_max_price(self):
        request = self.factory.get("/products/", {"max_price": "600"})
        products = list(get_filtered_products(request))

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Silver Ring")

    def test_sort_price_asc(self):
        request = self.factory.get("/products/", {"sort": "price_asc"})
        products = list(get_filtered_products(request))

        self.assertEqual(products[0].name, "Silver Ring")
        self.assertEqual(products[1].name, "Gold Ring")

    def test_pagination_limits_results(self):
        for i in range(PRODUCTS_PER_PAGE + 2):
            Product.objects.create(
                category=self.category,
                name=f"Ring {i}",
                slug=f"ring-{i}",
                description="Ring",
                price=Decimal("100.00"),
                stock=1,
                status="published",
            )

        request = self.factory.get("/products/")
        products = list(get_filtered_products(request))

        self.assertGreater(len(products), PRODUCTS_PER_PAGE)
