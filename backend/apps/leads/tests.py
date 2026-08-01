from django.core.management import call_command
from django.test import TestCase

from .models import CustomerRequest


class CustomerRequestApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

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

# Create your tests here.
