from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    


class Tag(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

class Product(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("out_of_stock", "Out of Stock"),
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(
        unique=True
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    material = models.CharField(
        max_length=100,
        blank=True
    )

    weight = models.CharField(
        max_length=50,
        blank=True
    )

    featured = models.BooleanField(
        default=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    tags = models.ManyToManyField(Tag, blank=True)

    seo_title = models.CharField(
    max_length=255,
    blank=True
    )

    seo_description = models.TextField(
        blank=True
    )

    @property
    def primary_image(self):
        primary = self.images.filter(
            is_primary=True
        ).first()

        return primary or self.images.first()
    
    @property
    def average_rating(self):

        reviews = self.reviews.filter(
            approved=True
        )

        if not reviews.exists():
            return 0

        return round(
            sum(r.rating for r in reviews) /
            reviews.count(),
            1
        )

    def __str__(self):
        return self.name

    @property
    def has_variants(self):
        return self.variants.exists()


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    metal = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    stone_color = models.CharField(max_length=50, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "id"]

    def __str__(self):
        parts = [p for p in (self.metal, self.size, self.stone_color) if p]
        label = " / ".join(parts) if parts else f"Variant #{self.pk}"
        return f"{self.product.name} — {label}"

    @property
    def display_label(self):
        parts = [p for p in (self.metal, self.size, self.stone_color) if p]
        return " / ".join(parts) if parts else "Standard"

    @property
    def effective_price(self):
        if self.discounted_price is not None:
            return self.discounted_price
        if self.price is not None:
            return self.price
        if self.product.discounted_price is not None:
            return self.product.discounted_price
        return self.product.price


class StockNotification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_notifications",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_notifications",
    )
    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("product", "variant", "email")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} — {self.product.name}"


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.product.name} Image"

