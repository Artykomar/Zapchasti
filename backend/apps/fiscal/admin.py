from django.contrib import admin, messages

from .models import FiscalReceipt, FiscalReceiptEvent, FiscalReceiptItem
from .services import retry_failed_receipt


class FiscalReceiptItemInline(admin.TabularInline):
    model = FiscalReceiptItem
    extra = 0


class FiscalReceiptEventInline(admin.TabularInline):
    model = FiscalReceiptEvent
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(FiscalReceipt)
class FiscalReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "critical_state", "payment", "order", "receipt_type", "status", "amount_rub", "currency", "created_at")
    list_filter = ("receipt_type", "status", "provider", "created_at")
    search_fields = ("=id", "=payment__id", "=order__id", "fiscal_number", "fiscal_document", "fiscal_sign")
    readonly_fields = ("fiscal_number", "fiscal_document", "fiscal_sign", "created_at", "updated_at")
    inlines = [FiscalReceiptItemInline, FiscalReceiptEventInline]
    actions = ["retry_failed_receipts"]

    @admin.display(boolean=True, description="Оплата прошла, чек не пробит")
    def critical_state(self, obj):
        return obj.payment.status == "succeeded" and obj.status == FiscalReceipt.Status.FAILED

    @admin.action(description="Retry selected failed receipts")
    def retry_failed_receipts(self, request, queryset):
        retried = 0
        for receipt in queryset.filter(status=FiscalReceipt.Status.FAILED):
            retry_failed_receipt(receipt)
            retried += 1
        self.message_user(request, f"Повторно поставлено в обработку: {retried}.", messages.SUCCESS)
