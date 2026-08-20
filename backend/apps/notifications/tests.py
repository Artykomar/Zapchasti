from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from apps.leads.models import CustomerRequest
from .models import NotificationDelivery
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

    def test_safe_notification_text_masks_personal_data(self):
        customer_request = CustomerRequest.objects.create(
            customer_name="Артём",
            contact="+7 999 111-22-33",
            vehicle="Skoda Octavia",
            request_text="Нужна фара",
            source=CustomerRequest.Source.REQUEST_FORM,
            privacy_accepted=True,
        )

        text = build_request_notification_text(customer_request, include_pii=False)

        self.assertIn(f"Новая заявка Zemazap #{customer_request.id}", text)
        self.assertIn("***2233", text)
        self.assertNotIn("Артём", text)
        self.assertNotIn("Skoda Octavia", text)
        self.assertNotIn("Нужна фара", text)

    @override_settings(
        ZEMAZAP_MANAGER_EMAIL="manager@example.ru",
        ZEMAZAP_TELEGRAM_CHAT_ID="",
        ZEMAZAP_TELEGRAM_BOT_TOKEN="",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_email_delivery_is_journaled(self):
        customer_request = CustomerRequest.objects.create(
            customer_name="Артём",
            contact="+7 999 111-22-33",
            request_text="Нужна фара",
            source=CustomerRequest.Source.REQUEST_FORM,
            privacy_accepted=True,
        )

        notify_manager_about_request(customer_request)

        delivery = NotificationDelivery.objects.get()
        self.assertEqual(delivery.status, NotificationDelivery.Status.SENT)
        self.assertEqual(delivery.safe_payload, {"request_id": customer_request.pk, "source": "request_form"})
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(
        ZEMAZAP_MANAGER_EMAIL="",
        ZEMAZAP_TELEGRAM_CHAT_ID="chat",
        ZEMAZAP_TELEGRAM_BOT_TOKEN="token",
        PII_IN_NOTIFICATIONS_ALLOWED=False,
    )
    @patch("apps.notifications.services.urllib_request.urlopen", side_effect=TimeoutError)
    def test_failed_external_delivery_has_retry_without_pii(self, _urlopen):
        customer_request = CustomerRequest.objects.create(
            customer_name="Артём",
            contact="+7 999 111-22-33",
            request_text="Нужна фара",
            source=CustomerRequest.Source.REQUEST_FORM,
            privacy_accepted=True,
        )

        notify_manager_about_request(customer_request)

        delivery = NotificationDelivery.objects.get()
        self.assertEqual(delivery.status, NotificationDelivery.Status.FAILED)
        self.assertIsNotNone(delivery.next_attempt_at)
        self.assertNotIn("Артём", str(delivery.safe_payload))
        self.assertNotIn("999", str(delivery.safe_payload))
