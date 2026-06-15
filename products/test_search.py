from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from products.models import Category, Product
from products.search_utils import get_did_you_mean, get_search_suggestions


class SearchTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Necklaces", slug="necklaces")
        self.product = Product.objects.create(
            category=self.category,
            name="Gold Necklace",
            slug="gold-necklace",
            description="Necklace",
            price=Decimal("1500.00"),
            stock=3,
            status="published",
        )

    def test_search_suggest_returns_results(self):
        response = self.client.get(reverse("search_suggest"), {"q": "gold"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["slug"], "gold-necklace")

    def test_search_suggest_requires_two_chars(self):
        response = self.client.get(reverse("search_suggest"), {"q": "g"})
        self.assertEqual(response.json(), [])

    def test_did_you_mean_suggestion_on_empty_results(self):
        Product.objects.create(
            category=self.category,
            name="Pearl Necklace",
            slug="pearl-necklace",
            description="Necklace",
            price=Decimal("1200.00"),
            stock=2,
            status="published",
        )
        suggestion = get_did_you_mean("pearl necklce")
        self.assertEqual(suggestion, "pearl necklace")

    def test_search_results_show_count_and_highlight(self):
        response = self.client.get(reverse("product_list"), {"q": "Gold"})
        self.assertContains(response, "1 result")
        self.assertContains(response, "search-highlight")

    def test_get_search_suggestions_helper(self):
        suggestions = get_search_suggestions("neck")
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["name"], "Gold Necklace")
