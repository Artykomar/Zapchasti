from __future__ import annotations

import logging
import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run payment, fiscal, notification and retention operations on a bounded schedule."

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval-seconds",
            type=int,
            default=settings.OPERATIONS_SCHEDULER_INTERVAL_SECONDS,
        )
        parser.add_argument(
            "--retention-interval-seconds",
            type=int,
            default=settings.OPERATIONS_RETENTION_INTERVAL_SECONDS,
        )
        parser.add_argument("--once", action="store_true")

    def _run_command(self, command_name: str, **options) -> None:
        try:
            call_command(command_name, **options)
        except Exception:
            logger.exception("Scheduled operation failed", extra={"command": command_name})

    def handle(self, *args, **options):
        interval = max(10, options["interval_seconds"])
        retention_interval = max(interval, options["retention_interval_seconds"])
        next_retention_at = 0.0

        while True:
            started_at = time.monotonic()
            self._run_command("reconcile_pending_payments")
            self._run_command("retry_failed_receipts")
            self._run_command("retry_notifications")
            self._run_command("sync_cdek_shipments")

            if started_at >= next_retention_at:
                self._run_command("anonymize_personal_data")
                next_retention_at = started_at + retention_interval

            if options["once"]:
                break
            time.sleep(max(1.0, interval - (time.monotonic() - started_at)))
