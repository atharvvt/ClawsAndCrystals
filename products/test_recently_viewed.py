from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from products.compare import MAX_COMPARE_ITEMS, add_to_compare, get_compare_ids
from products.models import Category, Product
from products.recently_viewed import get_recently_viewed_ids, track_view


class RecentlyViewedTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.product1 = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            description="Ring",
            price=Decimal("1000.00"),
            stock=5,
            status="published",
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name="Silver Ring",
            slug="silver-ring",
            description="Ring",
            price=Decimal("500.00"),
            stock=5,
            status="published",
        )

    def test_track_view_stores_ids_in_session(self):
        session = self.client.session
        request = type("Request", (), {"session": session})()
        track_view(request, self.product1.id)
        track_view(request, self.product2.id)
        session.save()

        self.assertEqual(get_recently_viewed_ids(request), [self.product2.id, self.product1.id])

    def test_product_detail_tracks_recently_viewed(self):
        self.client.get(reverse("product_detail", args=[self.product1.slug]))
        self.client.get(reverse("product_detail", args=[self.product2.slug]))
        response = self.client.get(reverse("product_detail", args=[self.product1.slug]))

        self.assertContains(response, "Recently Viewed")
        self.assertContains(response, self.product2.name)
