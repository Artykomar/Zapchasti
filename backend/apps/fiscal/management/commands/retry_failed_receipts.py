from django.core.management.base import BaseCommand

from apps.fiscal.models import FiscalReceipt
from apps.fiscal.services import retry_failed_receipt


class Command(BaseCommand):
    help = "Retry failed fiscal receipts using the configured provider."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        receipts = FiscalReceipt.objects.filter(status=FiscalReceipt.Status.FAILED).order_by("created_at")
        retried = 0
        for receipt in receipts[: max(1, options["limit"])]:
            retry_failed_receipt(receipt)
            retried += 1
        self.stdout.write(f"Retried {retried} receipt(s).")
