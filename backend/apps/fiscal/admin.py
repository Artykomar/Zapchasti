from django.contrib import admin

from .models import FiscalReceipt, FiscalReceiptEvent, FiscalReceiptItem


class FiscalReceiptItemInline(admin.TabularInline):
    model = FiscalReceiptItem
    extra = 0


class FiscalReceiptEventInline(admin.TabularInline):
    model = FiscalReceiptEvent
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(FiscalReceipt)
class FiscalReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "payment", "order", "receipt_type", "status", "amount_rub", "currency", "created_at")
    list_filter = ("receipt_type", "status", "provider", "created_at")
    search_fields = ("=id", "=payment__id", "=order__id", "fiscal_number", "fiscal_document", "fiscal_sign")
    readonly_fields = ("fiscal_number", "fiscal_document", "fiscal_sign", "created_at", "updated_at")
    inlines = [FiscalReceiptItemInline, FiscalReceiptEventInline]
