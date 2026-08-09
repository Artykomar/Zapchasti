from rest_framework import serializers

from .models import Brand, CarModel, Category, Part, PriceOffer


class CarModelSerializer(serializers.ModelSerializer):
    generations = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = CarModel
        fields = ["name", "slug", "years", "generations"]


class BrandSerializer(serializers.ModelSerializer):
    models = CarModelSerializer(many=True, read_only=True)

    class Meta:
        model = Brand
        fields = ["name", "slug", "country", "models"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug", "description"]


class PriceOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceOffer
        fields = ["price_rub", "availability", "delivery", "stock", "is_primary", "updated_at"]


class PartSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    oem = serializers.CharField(source="primary_oem")
    article = serializers.CharField(source="primary_article")
    brand = serializers.CharField(source="brand.name")
    brandSlug = serializers.CharField(source="brand.slug")
    category = serializers.CharField(source="category.name")
    categorySlug = serializers.CharField(source="category.slug")
    manufacturer = serializers.CharField(source="manufacturer.name")
    model = serializers.CharField(source="model_name")
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    delivery = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    analogs = serializers.SerializerMethodField()
    compatibility = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = [
            "id",
            "slug",
            "name",
            "oem",
            "article",
            "manufacturer",
            "category",
            "categorySlug",
            "brand",
            "brandSlug",
            "model",
            "price",
            "availability",
            "delivery",
            "stock",
            "condition",
            "quality",
            "description",
            "analogs",
            "compatibility",
            "specs",
        ]

    def get_id(self, part: Part) -> str:
        return part.legacy_id or part.slug or str(part.pk)

    def get_primary_offer(self, part: Part) -> PriceOffer | None:
        for offer in part.price_offers.all():
            if offer.is_primary:
                return offer
        return None

    def get_price(self, part: Part) -> int:
        offer = self.get_primary_offer(part)
        return offer.price_rub if offer else 0

    def get_availability(self, part: Part) -> str:
        offer = self.get_primary_offer(part)
        return offer.availability if offer else "уточнить"

    def get_delivery(self, part: Part) -> str:
        offer = self.get_primary_offer(part)
        return offer.delivery if offer else ""

    def get_stock(self, part: Part) -> str:
        offer = self.get_primary_offer(part)
        return offer.stock if offer else ""

    def get_analogs(self, part: Part) -> list[str]:
        return [number.value for number in part.numbers.all() if number.kind == "analog"]

    def get_compatibility(self, part: Part) -> list[str]:
        return [item.label for item in part.compatibility.all()]

    def get_specs(self, part: Part) -> dict[str, str]:
        return {item.name: item.value for item in part.specs.all()}
