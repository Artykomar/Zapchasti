from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.catalog.models import Brand, Category, Part
from .models import PriceImport
from .services import PriceImportRow, import_price_rows, parse_price_import_file


class PriceImportCyrillicTests(TestCase):
    def test_cp1251_csv_with_russian_headers_and_values_is_parsed(self):
        content = (
            "Название;Артикул;Марка;Категория;Цена\n"
            "Фара левая;A-100;Шкода;Фары;12500\n"
        ).encode("cp1251")

        rows = parse_price_import_file("price.csv", content)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].name, "Фара левая")
        self.assertEqual(rows[0].article, "A-100")
        self.assertEqual(rows[0].brand, "Шкода")
        self.assertEqual(rows[0].category, "Фары")
        self.assertEqual(rows[0].price, 12500)

    def test_comma_csv_with_utf8_russian_headers_is_parsed(self):
        content = (
            "Название,Артикул,Марка,Категория,Цена\n"
            "Бампер передний,B-200,Тойота,Бамперы,27000\n"
        ).encode("utf-8")

        rows = parse_price_import_file("price.csv", content)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].name, "Бампер передний")
        self.assertEqual(rows[0].brand, "Тойота")
        self.assertEqual(rows[0].category, "Бамперы")

    def test_russian_brand_category_and_part_slugs_are_distinct(self):
        import_price_rows(
            "price.csv",
            "csv",
            [
                PriceImportRow(name="Фара левая", article="A-100", brand="Шкода", category="Фары"),
                PriceImportRow(name="Бампер передний", article="B-200", brand="Тойота", category="Бамперы"),
            ],
        )

        self.assertEqual(Brand.objects.get(name="Шкода").slug, "shkoda")
        self.assertEqual(Brand.objects.get(name="Тойота").slug, "toyota")
        self.assertEqual(Category.objects.get(name="Фары").slug, "fary")
        self.assertEqual(Category.objects.get(name="Бамперы").slug, "bampery")
        self.assertTrue(Part.objects.filter(slug="a-100-fara-levaya").exists())
        self.assertTrue(Part.objects.filter(slug="b-200-bamper-peredniy").exists())
        self.assertNotEqual(
            Brand.objects.get(name="Шкода").slug,
            Brand.objects.get(name="Тойота").slug,
        )
        self.assertNotEqual(
            Category.objects.get(name="Фары").slug,
            Category.objects.get(name="Бамперы").slug,
        )


class PriceImportApiTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="manager",
            password="test-password",
            is_staff=True,
        )

    def test_import_endpoint_requires_staff_user(self):
        upload = SimpleUploadedFile(
            "price.csv",
            "Название;Артикул\nФара;A-100\n".encode("utf-8"),
            content_type="text/csv",
        )

        response = self.client.post("/api/imports/prices/", {"file": upload})

        self.assertEqual(response.status_code, 403)

    def test_bad_xlsx_returns_400_without_database_write(self):
        self.client.force_login(self.staff_user)
        upload = SimpleUploadedFile(
            "broken.xlsx",
            b"not a real xlsx file",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        response = self.client.post("/api/imports/prices/", {"file": upload})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(PriceImport.objects.count(), 0)
        self.assertEqual(Part.objects.count(), 0)

    def test_unsupported_file_type_returns_400(self):
        self.client.force_login(self.staff_user)
        upload = SimpleUploadedFile("price.txt", b"hello", content_type="text/plain")

        response = self.client.post("/api/imports/prices/", {"file": upload})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PriceImport.objects.count(), 0)
