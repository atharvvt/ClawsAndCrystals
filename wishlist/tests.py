from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from products.models import Category, Product
from wishlist.models import Wishlist, WishlistShare


class WishlistEnhancementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="wishuser",
            password="pass12345",
            first_name="Asha",
        )
        self.category = Category.objects.create(name="Bangles", slug="bangles")
        self.product = Product.objects.create(
            category=self.category,
            name="Gold Bangle",
            slug="gold-bangle",
            description="Bangle",
            price=Decimal("900.00"),
            stock=5,
            status="published",
        )
        Wishlist.objects.create(user=self.user, product=self.product)

    def test_toggle_wishlist_post(self):
        self.client.login(username="wishuser", password="pass12345")
        response = self.client.post(reverse("toggle_wishlist", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Wishlist.objects.filter(user=self.user, product=self.product).exists())

    def test_move_wishlist_item_to_cart(self):
        self.client.login(username="wishuser", password="pass12345")
        response = self.client.post(reverse("wishlist_add_to_cart", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("cart"))
        self.assertFalse(Wishlist.objects.filter(user=self.user, product=self.product).exists())

    def test_add_all_wishlist_to_cart(self):
        self.client.login(username="wishuser", password="pass12345")
        response = self.client.post(reverse("wishlist_add_all_to_cart"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("wishlist"))

    def test_generate_and_view_shared_wishlist(self):
        self.client.login(username="wishuser", password="pass12345")
        self.client.post(reverse("wishlist_share_generate"))
        share = WishlistShare.objects.get(user=self.user)

        response = self.client.get(reverse("wishlist_share", args=[share.token]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asha")
        self.assertContains(response, "Gold Bangle")
