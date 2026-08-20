from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from apps.payments.models import Payment
from apps.payments.services import synchronize_payment_status


class Command(BaseCommand):
    help = "Reconcile pending real-provider payments server-to-server."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        queryset = Payment.objects.filter(status=Payment.Status.PENDING).exclude(mode="test").order_by("created_at")
        checked = 0
        failed = 0
        for payment in queryset[: max(1, options["limit"])]:
            try:
                synchronize_payment_status(payment)
                checked += 1
            except ValidationError as exc:
                failed += 1
                self.stderr.write(f"Payment {payment.pk}: {'; '.join(exc.messages)}")
        self.stdout.write(f"Checked {checked} payment(s); failed {failed}.")
