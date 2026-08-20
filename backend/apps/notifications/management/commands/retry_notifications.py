from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import NotificationDelivery
from apps.notifications.services import deliver_notification


class Command(BaseCommand):
    help = "Retry failed notification deliveries whose backoff period has elapsed."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        deliveries = NotificationDelivery.objects.filter(
            status=NotificationDelivery.Status.FAILED,
            next_attempt_at__lte=timezone.now(),
        ).order_by("next_attempt_at")
        processed = 0
        for delivery in deliveries[: max(1, options["limit"])]:
            deliver_notification(delivery)
            processed += 1
        self.stdout.write(f"Retried {processed} notification(s).")
