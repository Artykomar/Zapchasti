from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Brand, Category, Part
from .serializers import BrandSerializer, CategorySerializer, PartSerializer
from .services import normalize_part_number


def filtered_parts(request):
    parts = (
        Part.objects.filter(is_active=True)
        .select_related("brand", "category", "manufacturer")
        .prefetch_related("numbers", "compatibility", "specs", "price_offers")
    )

    query = request.query_params.get("q", "").strip()
    brand = request.query_params.get("brand", "").strip()
    category = request.query_params.get("category", "").strip()
    condition = request.query_params.get("condition", "").strip()

    if query:
        parts = parts.filter(search_text__icontains=query.lower())
    if brand and brand != "all":
        parts = parts.filter(brand__slug=brand)
    if category and category != "all":
        parts = parts.filter(category__slug=category)
    if condition and condition != "all":
        parts = parts.filter(condition=condition)

    try:
        limit = int(request.query_params.get("limit", 100))
    except ValueError:
        limit = 100

    return parts[: max(1, min(limit, 200))]


class CatalogListAPIView(APIView):
    def get(self, request):
        brands = Brand.objects.prefetch_related("models__generations").all()
        categories = Category.objects.all()

        return Response(
            {
                "brands": BrandSerializer(brands, many=True).data,
                "categories": CategorySerializer(categories, many=True).data,
                "parts": PartSerializer(filtered_parts(request), many=True).data,
                "meta": {
                    "backend": "django",
                    "database": "sqlite-development",
                    "productionTarget": "postgresql",
                },
            }
        )


class CatalogDetailAPIView(APIView):
    def get(self, request, slug: str):
        normalized_number = normalize_part_number(slug)
        part = (
            Part.objects.filter(is_active=True)
            .filter(
                Q(slug=slug)
                | Q(legacy_id=slug)
                | Q(primary_article__iexact=slug)
                | Q(numbers__normalized_value=normalized_number)
            )
            .select_related("brand", "category", "manufacturer")
            .prefetch_related("numbers", "compatibility", "specs", "price_offers")
            .distinct()
            .first()
        )

        if not part:
            return Response({"error": "Part not found"}, status=404)

        return Response({"part": PartSerializer(part).data})

# Create your views here.
