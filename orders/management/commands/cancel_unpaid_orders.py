from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order


class Command(BaseCommand):
    help = "Cancel unpaid orders older than 48 hours"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=48,
            help="Cancel unpaid orders older than this many hours (default: 48)",
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=options["hours"])

        stale_orders = Order.objects.filter(
            payment_status="unpaid",
            created_at__lt=cutoff,
        ).exclude(status="cancelled")

        count = stale_orders.count()
        stale_orders.update(status="cancelled")

        self.stdout.write(
            self.style.SUCCESS(f"Cancelled {count} unpaid order(s) older than {options['hours']}h")
        )
