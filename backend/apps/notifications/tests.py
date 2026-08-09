from django.test import TestCase, override_settings

from apps.leads.models import CustomerRequest
from .services import build_request_notification_text, notify_manager_about_request


class NotificationServiceTests(TestCase):
    @override_settings(
        ZEMAZAP_MANAGER_EMAIL="",
        ZEMAZAP_TELEGRAM_CHAT_ID="",
        ZEMAZAP_TELEGRAM_BOT_TOKEN="",
    )
    def test_notification_without_channels_is_noop(self):
        customer_request = CustomerRequest.objects.create(
            customer_name="Артём",
            contact="+7 999 111-22-33",
            request_text="Нужна фара",
            source=CustomerRequest.Source.REQUEST_FORM,
            privacy_accepted=True,
        )

        notify_manager_about_request(customer_request)

        self.assertEqual(CustomerRequest.objects.count(), 1)

    def test_notification_text_contains_request_details(self):
        customer_request = CustomerRequest.objects.create(
            customer_name="Артём",
            contact="+7 999 111-22-33",
            vehicle="Skoda Octavia",
            request_text="Нужна фара",
            source=CustomerRequest.Source.REQUEST_FORM,
            privacy_accepted=True,
        )

        text = build_request_notification_text(customer_request)

        self.assertIn("Новая заявка Zemazap", text)
        self.assertIn("Артём", text)
        self.assertIn("Skoda Octavia", text)
