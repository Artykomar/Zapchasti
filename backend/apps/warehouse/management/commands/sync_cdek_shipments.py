from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.warehouse.cdek import sync_shipment
from apps.warehouse.models import Shipment


class Command(BaseCommand):
    help = "Reconcile a bounded batch of existing CDEK shipments; never create or dispatch orders."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=25)

    def handle(self, *args, **options):
        if not settings.CDEK_ENABLED:
            self.stdout.write("CDEK disabled; no external requests.")
            return
        rows = Shipment.objects.filter(mode=settings.CDEK_MODE).exclude(
            status__in=[Shipment.Status.DRAFT, Shipment.Status.DELIVERED, Shipment.Status.CANCELLED]
        ).order_by("updated_at", "pk")[:max(1, min(options["limit"], 50))]
        succeeded = failed = 0
        for shipment in rows:
            try:
                sync_shipment(shipment.pk)
                succeeded += 1
            except ValidationError as exc:
                Shipment.objects.filter(pk=shipment.pk, updated_at=shipment.updated_at).update(
                    last_error="; ".join(exc.messages)[:240], updated_at=timezone.now())
                failed += 1
        self.stdout.write(f"CDEK reconciled: {succeeded}; attention needed: {failed}.")
