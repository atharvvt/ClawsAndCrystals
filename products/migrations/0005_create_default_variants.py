from decimal import Decimal

from django.db import migrations


def create_default_variants(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    ProductVariant = apps.get_model("products", "ProductVariant")

    for product in Product.objects.all():
        if ProductVariant.objects.filter(product=product).exists():
            continue

        ProductVariant.objects.create(
            product=product,
            metal=product.material or "",
            sku=product.sku,
            price=product.price,
            discounted_price=product.discounted_price,
            stock=product.stock,
            is_default=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_productvariant_stocknotification"),
    ]

    operations = [
        migrations.RunPython(create_default_variants, migrations.RunPython.noop),
    ]
