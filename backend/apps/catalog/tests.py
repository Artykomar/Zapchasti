from django.core.management import call_command
from django.test import TestCase

from .models import Brand, Part


class CatalogApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def test_seed_demo_loads_catalog(self):
        self.assertEqual(Brand.objects.count(), 10)
        self.assertEqual(Part.objects.count(), 12)

    def test_catalog_api_uses_next_compatible_shape(self):
        response = self.client.get("/api/catalog/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("brands", payload)
        self.assertIn("categories", payload)
        self.assertIn("parts", payload)
        self.assertEqual(payload["parts"][0]["id"], "octavia-led-headlamp-left")
        self.assertIn("categorySlug", payload["parts"][0])
        self.assertIn("brandSlug", payload["parts"][0])

    def test_catalog_api_uses_bounded_query_count(self):
        with self.assertNumQueries(9):
            response = self.client.get("/api/catalog/?limit=12")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["parts"]), 12)

    def test_catalog_search_handles_hostile_input_safely(self):
        response = self.client.get("/api/catalog/?q='; DROP TABLE catalog_part; --")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["parts"], [])
        self.assertEqual(Part.objects.count(), 12)

# Create your tests here.
