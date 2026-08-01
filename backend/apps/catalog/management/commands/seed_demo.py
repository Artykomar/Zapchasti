from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Brand, CarModel, Category, ModelGeneration, Supplier
from apps.catalog.services import upsert_demo_part


class Command(BaseCommand):
    help = "Seed the Django database with the Zemazap demo catalog."

    def handle(self, *args, **options):
        data_path = Path(__file__).resolve().parents[2] / "demo_data.json"
        data = json.loads(data_path.read_text(encoding="utf-8"))

        with transaction.atomic():
            supplier, _created = Supplier.objects.update_or_create(
                name="Демо-поставщик Zemazap",
                defaults={
                    "kind": "demo",
                    "contact_note": "Временный источник цен и сроков для MVP",
                },
            )

            for brand_index, brand_data in enumerate(data["brands"]):
                brand, _created = Brand.objects.update_or_create(
                    slug=brand_data["slug"],
                    defaults={
                        "name": brand_data["name"],
                        "country": brand_data["country"],
                        "sort_order": brand_index,
                    },
                )
                for model_index, model_data in enumerate(brand_data["models"]):
                    car_model, _created = CarModel.objects.update_or_create(
                        brand=brand,
                        slug=model_data["slug"],
                        defaults={
                            "name": model_data["name"],
                            "years": model_data["years"],
                            "sort_order": model_index,
                        },
                    )
                    car_model.generations.all().delete()
                    ModelGeneration.objects.bulk_create(
                        ModelGeneration(car_model=car_model, name=name, sort_order=index)
                        for index, name in enumerate(model_data["generations"])
                    )

            for category_index, category_data in enumerate(data["categories"]):
                Category.objects.update_or_create(
                    slug=category_data["slug"],
                    defaults={
                        "name": category_data["name"],
                        "description": category_data["description"],
                        "sort_order": category_index,
                    },
                )

            for part_index, part_data in enumerate(data["parts"]):
                upsert_demo_part(
                    legacy_id=part_data["legacy_id"],
                    slug=part_data["slug"],
                    name=part_data["name"],
                    oem=part_data["oem"],
                    article=part_data["article"],
                    manufacturer_name=part_data["manufacturer"],
                    category_slug=part_data["category_slug"],
                    category_name=part_data["category_name"],
                    brand_slug=part_data["brand_slug"],
                    brand_name=part_data["brand_name"],
                    model_name=part_data["model"],
                    compatibility=part_data["compatibility"],
                    price=part_data["price"],
                    availability=part_data["availability"],
                    delivery=part_data["delivery"],
                    analogs=part_data["analogs"],
                    condition=part_data["condition"],
                    quality=part_data["quality"],
                    stock=part_data["stock"],
                    description=part_data["description"],
                    specs=part_data["specs"],
                    supplier=supplier,
                    sort_order=part_index,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(data['brands'])} brands, {len(data['categories'])} categories and {len(data['parts'])} parts."
            )
        )
