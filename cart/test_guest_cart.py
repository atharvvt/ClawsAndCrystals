from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from cart.models import CartItem
from cart.session_cart import get_session_cart_count
from products.models import Category, Product, ProductVariant


class GuestCartTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            description="Test ring",
            price=Decimal("1500.00"),
            stock=5,
            status="published",
        )

    def test_guest_can_add_to_cart(self):
        response = self.client.get(reverse("add_to_cart", args=[self.product.id]))

        self.assertEqual(response.status_code, 302)
        session = self.client.session
        session.save()
        self.assertEqual(get_session_cart_count(session), 1)

    def test_guest_cart_merges_on_login(self):
        self.client.get(reverse("add_to_cart", args=[self.product.id]))
        User.objects.create_user(
            username="buyer",
            password="testpass123",
        )

        self.client.post(
            reverse("login"),
            {"username": "buyer", "password": "testpass123"},
        )

        self.assertEqual(CartItem.objects.filter(user__username="buyer").count(), 1)
        self.assertEqual(CartItem.objects.get(user__username="buyer").quantity, 1)
