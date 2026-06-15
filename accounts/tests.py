from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import ShippingAddress, UserProfile
from orders.forms import CheckoutForm
from orders.models import Order, OrderItem
from orders.payments import mark_order_paid
from products.models import Category, Product


class ShippingAddressTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="testpass123",
        )

    def test_only_one_default_address_per_user(self):
        ShippingAddress.objects.create(
            user=self.user,
            label="Home",
            full_name="Buyer",
            email="buyer@example.com",
            phone="9876543210",
            address="123 Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            is_default=True,
        )

        ShippingAddress.objects.create(
            user=self.user,
            label="Office",
            full_name="Buyer",
            email="buyer@example.com",
            phone="9876543210",
            address="456 Avenue",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            is_default=True,
        )

        defaults = ShippingAddress.objects.filter(
            user=self.user,
            is_default=True,
        )

        self.assertEqual(defaults.count(), 1)
        self.assertEqual(defaults.first().label, "Office")


class CheckoutValidationTest(TestCase):

    def test_rejects_invalid_phone(self):
        form = CheckoutForm(
            data={
                "full_name": "Buyer",
                "email": "buyer@example.com",
                "phone": "12345",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "address": "123 Long Street Name Here",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_rejects_invalid_pincode(self):
        form = CheckoutForm(
            data={
                "full_name": "Buyer",
                "email": "buyer@example.com",
                "phone": "9876543210",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "ABC",
                "address": "123 Long Street Name Here",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("pincode", form.errors)

    def test_normalizes_phone_spaces(self):
        form = CheckoutForm(
            data={
                "full_name": "Buyer",
                "email": "buyer@example.com",
                "phone": "98765 43210",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "address": "123 Long Street Name Here",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["phone"], "9876543210")


class StockDecrementTest(TestCase):

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
            stock=3,
            status="published",
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="9876543210",
            address="123 Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            total_amount=Decimal("3000.00"),
            razorpay_order_id="order_test123",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal("1500.00"),
        )

    def test_mark_order_paid_decrements_stock(self):
        mark_order_paid(self.order, "pay_test123")

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)
        self.assertEqual(self.product.status, "published")

    def test_mark_order_paid_sets_out_of_stock(self):
        self.product.stock = 2
        self.product.save()

        mark_order_paid(self.order, "pay_test123")

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
        self.assertEqual(self.product.status, "out_of_stock")


class SavedAddressCheckoutTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="testpass123",
        )

    def test_save_address_on_checkout(self):
        from orders.views import _save_shipping_address

        form_data = {
            "full_name": "Buyer",
            "email": "buyer@example.com",
            "phone": "9876543210",
            "address": "123 Long Street Name Here",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "save_address": True,
            "address_label": "Home",
        }

        _save_shipping_address(self.user, form_data)

        address = ShippingAddress.objects.get(user=self.user)
        self.assertEqual(address.label, "Home")
        self.assertTrue(address.is_default)


class ProfileViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="testpass123",
        )
        self.client = Client()
        self.client.login(username="buyer", password="testpass123")

    def test_profile_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_dashboard_loads(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back")

    def test_profile_edit_updates_user(self):
        response = self.client.post(
            reverse("profile_edit"),
            {
                "first_name": "Priya",
                "last_name": "Sharma",
                "email": "priya@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Priya")
        self.assertEqual(self.user.email, "priya@example.com")

    def test_profile_password_change(self):
        response = self.client.post(
            reverse("profile_password"),
            {
                "old_password": "testpass123",
                "new_password1": "newpass456!",
                "new_password2": "newpass456!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass456!"))

    def test_profile_creates_user_profile(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_add_address_from_profile(self):
        response = self.client.post(
            reverse("profile_address_add"),
            {
                "label": "Home",
                "full_name": "Buyer",
                "email": "buyer@example.com",
                "phone": "9876543210",
                "address": "123 Long Street Name Here",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "is_default": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ShippingAddress.objects.filter(user=self.user).count(), 1)
