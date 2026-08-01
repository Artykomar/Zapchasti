from django.contrib import admin

from .models import PriceImport


@admin.register(PriceImport)
class PriceImportAdmin(admin.ModelAdmin):
    list_display = ("filename", "file_kind", "imported_rows", "skipped_rows", "created_at")
    search_fields = ("filename", "file_kind")

# Register your models here.
