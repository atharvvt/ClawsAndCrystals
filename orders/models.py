from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    address = models.TextField()

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="unpaid"
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id}"
    

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product.name