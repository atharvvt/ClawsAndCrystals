from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cart.models import CartItem
from products.models import Category, Product


class CartStockTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            password="testpass123",
        )
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            description="Test ring",
            price=Decimal("1500.00"),
            stock=2,
            status="published",
        )
        self.client.login(username="buyer", password="testpass123")

    def test_add_to_cart_blocked_when_out_of_stock(self):
        self.product.stock = 0
        self.product.save()

        response = self.client.get(
            reverse("add_to_cart", args=[self.product.id]),
        )

        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        self.assertEqual(response.status_code, 302)

    def test_increase_quantity_capped_at_stock(self):
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )

        self.client.get(reverse("increase_quantity", args=[cart_item.id]))

        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)
