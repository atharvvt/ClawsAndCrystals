from django.db import models
from django.shortcuts import (
    render,
    get_object_or_404,
)

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

    def __str__(self):
        return self.name


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
    

def category_products(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug
    )

    categories = Category.objects.all()

    products = Product.objects.filter(
        category=category,
        status="published"
    )

    return render(
        request,
        "product/product_list.html",
        {
            "products": products,
            "category": category,
            "categories": categories,

        }
    )