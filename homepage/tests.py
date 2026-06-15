from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from homepage.models import HomepageBanner, HomepageFeature, Testimonial


class HomepageCMSTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_models_render(self):
        HomepageBanner.objects.create(
            title="Test Hero",
            subtitle="Test subtitle",
            cta_text="Shop Now",
            cta_url="/products/",
            is_active=True,
        )
        Testimonial.objects.create(
            name="Riya K.",
            location="Chennai",
            quote="Lovely designs.",
            rating=5,
            is_active=True,
        )
        HomepageFeature.objects.create(
            icon="✦",
            title="Quality",
            description="Premium quality jewellery.",
            is_active=True,
        )

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Hero")
        self.assertContains(response, "Riya K.")
        self.assertContains(response, "Quality")

    def test_seed_homepage_command(self):
        call_command("seed_homepage")
        self.assertTrue(HomepageBanner.objects.exists())
        self.assertEqual(Testimonial.objects.count(), 2)
        self.assertEqual(HomepageFeature.objects.count(), 4)
