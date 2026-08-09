from django.core.management import call_command
from django.core.cache import cache
from django.test import TestCase

from .models import CustomerRequest


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

# Create your tests here.
