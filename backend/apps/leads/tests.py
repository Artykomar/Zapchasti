from django.core.management import call_command
from django.core.cache import cache
from django.test import TestCase, override_settings

from .models import CustomerRequest
from .services import anonymize_customer_request


class CustomerRequestApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def setUp(self):
        cache.clear()

    def test_request_api_creates_customer_request(self):
        response = self.client.post(
            "/api/requests/",
            data={
                "customerName": "Артём",
                "contact": "+7 999 111-22-33",
                "vehicle": "Skoda Octavia A7",
                "requestText": "",
                "source": "cart",
                "privacyAccepted": True,
                "items": [
                    {
                        "id": "octavia-led-headlamp-left",
                        "name": "Фара светодиодная левая",
                        "article": "ZP-LGT-5015L",
                        "quantity": 1,
                        "price": 34700,
                    }
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomerRequest.objects.count(), 1)
        self.assertEqual(CustomerRequest.objects.first().items.count(), 1)
        customer_request = CustomerRequest.objects.first()
        self.assertEqual(customer_request.privacy_policy_version, "draft-2026-08-15")
        self.assertEqual(customer_request.privacy_consent_version, "draft-2026-08-15")
        self.assertEqual(customer_request.consent_source, "cart")
        self.assertIsNotNone(customer_request.consent_accepted_at)

    @override_settings(
        ZEMAZAP_PRIVACY_POLICY_VERSION="policy-v2",
        ZEMAZAP_PRIVACY_CONSENT_VERSION="consent-v2",
    )
    def test_request_api_captures_consent_metadata(self):
        response = self.client.post(
            "/api/requests/",
            data={
                "customerName": "Артём",
                "contact": "+7 999 111-22-33",
                "requestText": "Нужна фара",
                "source": "request_form",
                "privacyAccepted": True,
                "consentSource": "request_form",
            },
            content_type="application/json",
            HTTP_USER_AGENT="Zemazap test browser",
            HTTP_X_FORWARDED_FOR="203.0.113.10",
        )

        self.assertEqual(response.status_code, 201)
        customer_request = CustomerRequest.objects.get()
        self.assertEqual(customer_request.privacy_policy_version, "policy-v2")
        self.assertEqual(customer_request.privacy_consent_version, "consent-v2")
        self.assertEqual(customer_request.consent_source, "request_form")
        self.assertEqual(customer_request.consent_ip, "203.0.113.10")
        self.assertEqual(customer_request.consent_user_agent, "Zemazap test browser")

    def test_request_api_rejects_overlong_text(self):
        response = self.client.post(
            "/api/requests/",
            data={
                "customerName": "Артём",
                "contact": "+7 999 111-22-33",
                "requestText": "x" * 5000,
                "source": "request_form",
                "privacyAccepted": True,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CustomerRequest.objects.count(), 0)

    def test_request_api_rejects_too_many_cart_items(self):
        response = self.client.post(
            "/api/requests/",
            data={
                "customerName": "Артём",
                "contact": "+7 999 111-22-33",
                "requestText": "Корзина",
                "source": "cart",
                "privacyAccepted": True,
                "items": [
                    {
                        "name": f"Позиция {index}",
                        "article": f"A-{index}",
                        "quantity": 1,
                        "price": 1000,
                    }
                    for index in range(75)
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CustomerRequest.objects.count(), 0)

    def test_request_api_rejects_honeypot_payload(self):
        response = self.client.post(
            "/api/requests/",
            data={
                "customerName": "Артём",
                "contact": "+7 999 111-22-33",
                "requestText": "Нужна фара",
                "source": "request_form",
                "privacyAccepted": True,
                "website": "https://spam.example",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CustomerRequest.objects.count(), 0)

    def test_request_api_has_separate_rate_limit(self):
        cache.clear()
        payload = {
            "customerName": "Артём",
            "contact": "+7 999 111-22-33",
            "requestText": "Нужна фара",
            "source": "request_form",
            "privacyAccepted": True,
        }

        responses = [
            self.client.post("/api/requests/", data=payload, content_type="application/json")
            for _index in range(11)
        ]

        self.assertTrue(all(response.status_code == 201 for response in responses[:10]))
        self.assertEqual(responses[-1].status_code, 429)

    def test_request_personal_data_can_be_anonymized_idempotently(self):
        customer_request = CustomerRequest.objects.create(
            customer_name="Артём",
            contact="+7 999 111-22-33",
            vehicle="Skoda Octavia",
            request_text="Нужна фара",
            source=CustomerRequest.Source.REQUEST_FORM,
            privacy_accepted=True,
            consent_ip="203.0.113.10",
            consent_user_agent="Test browser",
        )

        anonymize_customer_request(customer_request, reason="Test")
        anonymize_customer_request(customer_request, reason="Duplicate")

        customer_request.refresh_from_db()
        self.assertEqual(customer_request.customer_name, "Удалено")
        self.assertNotIn("999", customer_request.contact)
        self.assertEqual(customer_request.vehicle, "")
        self.assertEqual(customer_request.request_text, "")
        self.assertIsNone(customer_request.consent_ip)
        self.assertIsNotNone(customer_request.anonymized_at)

# Create your tests here.
