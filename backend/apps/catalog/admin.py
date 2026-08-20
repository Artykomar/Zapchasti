from django.contrib import admin

from .models import (
    Brand,
    CarModel,
    Category,
    Manufacturer,
    ModelGeneration,
    Part,
    PartCompatibility,
    PartDocument,
    PartNumber,
    PartSpec,
    PriceOffer,
    Supplier,
)


class ModelGenerationInline(admin.TabularInline):
    model = ModelGeneration
    extra = 0


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "country", "sort_order")
    search_fields = ("name", "slug", "country")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "years", "sort_order")
    list_filter = ("brand",)
    search_fields = ("name", "slug", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ModelGenerationInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "updated_at")
    search_fields = ("name", "kind", "contact_note")


class PartNumberInline(admin.TabularInline):
    model = PartNumber
    extra = 0


class PartCompatibilityInline(admin.TabularInline):
    model = PartCompatibility
    extra = 0


class PartSpecInline(admin.TabularInline):
    model = PartSpec
    extra = 0


class PriceOfferInline(admin.TabularInline):
    model = PriceOffer
    extra = 0


class PartDocumentInline(admin.TabularInline):
    model = PartDocument
    extra = 0


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "legacy_id",
        "brand",
        "category",
        "condition",
        "marking_status",
        "sale_blocked_by_marking",
        "primary_article",
        "is_active",
    )
    list_filter = ("is_active", "brand", "category", "condition", "photo_kind", "marking_required", "marking_status")
    search_fields = ("name", "legacy_id", "primary_oem", "primary_article", "search_text")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PartNumberInline, PartCompatibilityInline, PartSpecInline, PartDocumentInline, PriceOfferInline]

# Register your models here.
