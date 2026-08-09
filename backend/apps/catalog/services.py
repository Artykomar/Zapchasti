from __future__ import annotations

import re

from django.db import transaction
from django.utils.text import slugify

from .models import (
    Brand,
    CarModel,
    Category,
    Manufacturer,
    ModelGeneration,
    Part,
    PartCompatibility,
    PartNumber,
    PartSpec,
    PriceOffer,
    Supplier,
)

CYRILLIC_TRANSLITERATION = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def normalize_search(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def normalize_part_number(value: str) -> str:
    return re.sub(r"[\s_-]+", "", normalize_search(value))


def build_part_search_text(
    *,
    name: str,
    oem: str,
    article: str,
    manufacturer: str,
    category: str,
    brand: str,
    model: str,
    condition: str,
    quality: str,
    analogs: list[str],
    compatibility: list[str],
    specs: dict[str, str],
) -> str:
    parts = [
        name,
        oem,
        article,
        manufacturer,
        category,
        brand,
        model,
        condition,
        quality,
        normalize_part_number(oem),
        normalize_part_number(article),
        *analogs,
        *(normalize_part_number(item) for item in analogs),
        *compatibility,
        *specs.values(),
    ]
    return normalize_search(" ".join(item for item in parts if item))


def transliterate_cyrillic(value: str) -> str:
    return "".join(CYRILLIC_TRANSLITERATION.get(char.lower(), char) for char in value)


def stable_slug(value: str, fallback: str = "item", max_length: int | None = None) -> str:
    slug = slugify(transliterate_cyrillic(value), allow_unicode=False)

    if max_length is not None:
        slug = slug[:max_length].strip("-")

    return slug or fallback


@transaction.atomic
def upsert_demo_part(
    *,
    legacy_id: str,
    slug: str,
    name: str,
    oem: str,
    article: str,
    manufacturer_name: str,
    category_slug: str,
    category_name: str,
    brand_slug: str,
    brand_name: str,
    model_name: str,
    compatibility: list[str],
    price: int,
    availability: str,
    delivery: str,
    analogs: list[str],
    condition: str,
    quality: str,
    stock: str,
    description: str,
    specs: dict[str, str],
    supplier: Supplier,
    sort_order: int,
) -> Part:
    brand = Brand.objects.get(slug=brand_slug)
    category = Category.objects.get(slug=category_slug)
    manufacturer, _created = Manufacturer.objects.update_or_create(
        name=manufacturer_name,
        defaults={"name": manufacturer_name},
    )
    search_text = build_part_search_text(
        name=name,
        oem=oem,
        article=article,
        manufacturer=manufacturer_name,
        category=category_name,
        brand=brand_name,
        model=model_name,
        condition=condition,
        quality=quality,
        analogs=analogs,
        compatibility=compatibility,
        specs=specs,
    )
    part, _created = Part.objects.update_or_create(
        slug=slug,
        defaults={
            "legacy_id": legacy_id,
            "name": name,
            "category": category,
            "brand": brand,
            "model_name": model_name,
            "manufacturer": manufacturer,
            "condition": condition,
            "quality": quality,
            "description": description,
            "primary_oem": oem,
            "primary_article": article,
            "search_text": search_text,
            "is_active": True,
            "sort_order": sort_order,
        },
    )

    part.numbers.all().delete()
    part.compatibility.all().delete()
    part.specs.all().delete()
    part.price_offers.all().delete()

    numbers = [
        PartNumber(part=part, kind=PartNumber.Kind.OEM, value=oem, normalized_value=normalize_part_number(oem), sort_order=0),
        PartNumber(
            part=part,
            kind=PartNumber.Kind.ARTICLE,
            value=article,
            normalized_value=normalize_part_number(article),
            sort_order=1,
        ),
    ]
    numbers.extend(
        PartNumber(
            part=part,
            kind=PartNumber.Kind.ANALOG,
            value=analog,
            normalized_value=normalize_part_number(analog),
            sort_order=index + 2,
        )
        for index, analog in enumerate(analogs)
    )
    PartNumber.objects.bulk_create(numbers)
    PartCompatibility.objects.bulk_create(
        PartCompatibility(part=part, label=label, sort_order=index)
        for index, label in enumerate(compatibility)
    )
    PartSpec.objects.bulk_create(
        PartSpec(part=part, name=key, value=value, sort_order=index)
        for index, (key, value) in enumerate(specs.items())
    )
    PriceOffer.objects.create(
        part=part,
        supplier=supplier,
        price_rub=price,
        availability=availability,
        delivery=delivery,
        stock=stock,
        is_primary=True,
    )
    return part
