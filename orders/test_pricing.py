from decimal import Decimal

from django.test import TestCase

from cart.lines import SessionCartLine
from orders.pricing import compute_order_totals
from promotions.models import Coupon
from shipping.models import ShippingSettings


class PricingEngineTest(TestCase):

    def setUp(self):
        ShippingSettings.objects.create(
            flat_rate=Decimal("40.00"),
            free_shipping_threshold=Decimal("500.00"),
            is_active=True,
        )
        self.product = type(
            "Product",
            (),
            {
                "price": Decimal("300.00"),
                "discounted_price": None,
            },
        )()
        self.line = SessionCartLine(
            product=self.product,
            variant=None,
            quantity=1,
            session_key="session:1:0",
        )

    def test_shipping_charged_below_threshold(self):
        totals = compute_order_totals([self.line], pincode="400001", state="Maharashtra")

        self.assertEqual(totals.subtotal_amount, Decimal("300.00"))
        self.assertEqual(totals.shipping_amount, Decimal("40.00"))
        self.assertEqual(totals.total_amount, Decimal("340.00"))

    def test_free_shipping_above_threshold(self):
        self.line.quantity = 2
        totals = compute_order_totals([self.line], pincode="400001", state="Maharashtra")

        self.assertEqual(totals.shipping_amount, Decimal("0.00"))
        self.assertEqual(totals.total_amount, Decimal("600.00"))

    def test_save10_percent_discount(self):
        Coupon.objects.create(
            code="SAVE10",
            coupon_type=Coupon.TYPE_PERCENT,
            value=Decimal("10.00"),
            active=True,
        )

        totals = compute_order_totals(
            [self.line],
            coupon_code="SAVE10",
            pincode="400001",
            state="Maharashtra",
        )

        self.assertEqual(totals.discount_amount, Decimal("30.00"))
        self.assertEqual(totals.shipping_amount, Decimal("40.00"))
        self.assertEqual(totals.total_amount, Decimal("310.00"))

    def test_freeship_coupon_above_minimum(self):
        Coupon.objects.create(
            code="FREESHIP",
            coupon_type=Coupon.TYPE_FREE_SHIPPING,
            free_shipping_min=Decimal("500.00"),
            active=True,
        )
        self.line.quantity = 2

        totals = compute_order_totals(
            [self.line],
            coupon_code="FREESHIP",
            pincode="400001",
            state="Maharashtra",
        )

        self.assertEqual(totals.shipping_amount, Decimal("0.00"))
        self.assertEqual(totals.total_amount, Decimal("600.00"))
