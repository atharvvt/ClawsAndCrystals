from django.core.management.base import BaseCommand

from homepage.models import HomepageBanner, HomepageFeature, Testimonial


class Command(BaseCommand):
    help = "Seed default homepage CMS content"

    def handle(self, *args, **options):
        if not HomepageBanner.objects.exists():
            HomepageBanner.objects.create(
                title="Jewellery That Tells a Story",
                subtitle="Inspired by Indian traditions and crafted for modern elegance.",
                cta_text="Shop the Collection",
                cta_url="/products/",
                is_active=True,
                sort_order=0,
            )
            self.stdout.write("Created homepage banner")

        if not Testimonial.objects.exists():
            Testimonial.objects.create(
                name="Priya M.",
                location="Mumbai",
                quote="Beautiful craftsmanship and the most thoughtful packaging I've ever received.",
                rating=5,
                is_active=True,
                sort_order=0,
            )
            Testimonial.objects.create(
                name="Ananya S.",
                location="Delhi",
                quote="Stunning designs that perfectly complemented my lehenga.",
                rating=5,
                is_active=True,
                sort_order=1,
            )
            self.stdout.write("Created testimonials")

        if not HomepageFeature.objects.exists():
            features = [
                ("🪡", "Authentic Craftsmanship", "Each piece made by skilled artisans with decades of tradition."),
                ("💎", "Premium Materials", "Ethically sourced stones and metals of the highest quality."),
                ("✦", "Handpicked Designs", "Every design curated to balance heritage with modern taste."),
                ("📦", "Nationwide Delivery", "Swift, insured shipping to every corner of India."),
            ]
            for index, (icon, title, description) in enumerate(features):
                HomepageFeature.objects.create(
                    icon=icon,
                    title=title,
                    description=description,
                    is_active=True,
                    sort_order=index,
                )
            self.stdout.write("Created homepage features")

        self.stdout.write(self.style.SUCCESS("Homepage content seeded."))
