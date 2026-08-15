from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Brand(TimeStampedModel):
    slug = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    country = models.CharField(max_length=120, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class CarModel(TimeStampedModel):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="models")
    slug = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    years = models.CharField(max_length=80, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["brand__sort_order", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["brand", "slug"], name="unique_car_model_slug_per_brand")
        ]

    def __str__(self) -> str:
        return f"{self.brand} {self.name}"


class ModelGeneration(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name="generations")
    name = models.CharField(max_length=160)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return f"{self.car_model}: {self.name}"


class Category(TimeStampedModel):
    slug = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Manufacturer(TimeStampedModel):
    name = models.CharField(max_length=160, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=160)
    kind = models.CharField(max_length=80, default="demo")
    contact_note = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Part(TimeStampedModel):
    class Availability(models.TextChoices):
        IN_STOCK = "в наличии", "в наличии"
        DAYS_1_3 = "1-3 дня", "1-3 дня"
        PREORDER = "под заказ", "под заказ"
        CHECK = "уточнить", "уточнить"

    class Condition(models.TextChoices):
        NEW = "новая", "новая"
        CONTRACT = "контрактная", "контрактная"
        RESTORED = "восстановленная", "восстановленная"

    legacy_id = models.CharField(max_length=160, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=160, unique=True)
    name = models.CharField(max_length=240)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="parts")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="parts")
    model_name = models.CharField(max_length=160, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name="parts")
    condition = models.CharField(max_length=40, choices=Condition.choices, default=Condition.NEW)
    quality = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    fiscal_name = models.CharField(max_length=128, blank=True)
    vat_label = models.CharField(max_length=80, default="НДС не задан")
    payment_subject = models.CharField(max_length=80, default="commodity")
    payment_method = models.CharField(max_length=80, default="full_payment")
    unit = models.CharField(max_length=40, default="шт.")
    primary_oem = models.CharField(max_length=120, blank=True)
    primary_article = models.CharField(max_length=120, blank=True)
    search_text = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["brand", "category"]),
            models.Index(fields=["condition"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class PartNumber(models.Model):
    class Kind(models.TextChoices):
        OEM = "oem", "OEM"
        ARTICLE = "article", "article"
        ANALOG = "analog", "analog"

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="numbers")
    kind = models.CharField(max_length=40, choices=Kind.choices)
    value = models.CharField(max_length=120)
    normalized_value = models.CharField(max_length=120, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "value"]

    def __str__(self) -> str:
        return f"{self.kind}: {self.value}"


class PartCompatibility(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="compatibility")
    label = models.CharField(max_length=240)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "label"]
        verbose_name_plural = "part compatibility"

    def __str__(self) -> str:
        return self.label


class PartSpec(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="specs")
    name = models.CharField(max_length=120)
    value = models.CharField(max_length=240)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


class PriceOffer(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="price_offers")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="price_offers")
    price_rub = models.PositiveIntegerField(default=0)
    availability = models.CharField(max_length=40, choices=Part.Availability.choices, default=Part.Availability.CHECK)
    delivery = models.CharField(max_length=160, blank=True)
    stock = models.CharField(max_length=160, blank=True)
    is_primary = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["part", "-is_primary", "price_rub"]
        indexes = [
            models.Index(fields=["part", "is_primary"]),
        ]

    def __str__(self) -> str:
        return f"{self.part} - {self.price_rub} RUB"

# Create your models here.
