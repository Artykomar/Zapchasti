from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.core.models import RetentionPolicy
from apps.leads.models import CustomerRequest
from apps.leads.services import anonymize_customer_request


class Command(BaseCommand):
    help = "Anonymize expired or explicitly selected customer-request personal data."

    def add_arguments(self, parser):
        parser.add_argument("--request-id", action="append", type=int, dest="request_ids")
        parser.add_argument("--older-than-days", type=int)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        policy = RetentionPolicy.load()
        days = options["older_than_days"] or policy.request_retention_days
        if days < 1:
            raise CommandError("--older-than-days must be a positive integer.")

        queryset = CustomerRequest.objects.filter(anonymized_at__isnull=True)
        request_ids = options.get("request_ids") or []
        if request_ids:
            queryset = queryset.filter(pk__in=request_ids)
        else:
            queryset = queryset.filter(created_at__lt=timezone.now() - timedelta(days=days))

        candidates = list(queryset.order_by("pk"))
        if options["dry_run"]:
            self.stdout.write(f"Would anonymize {len(candidates)} request(s).")
            return

        for customer_request in candidates:
            anonymize_customer_request(customer_request, reason="Retention policy management command.")
        self.stdout.write(self.style.SUCCESS(f"Anonymized {len(candidates)} request(s)."))
