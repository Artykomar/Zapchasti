from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Claim, Refund, RefundEvent, RefundItem
from .services import process_refund


class RefundItemInline(admin.TabularInline):
    model = RefundItem
    extra = 0


class RefundEventInline(admin.TabularInline):
    model = RefundEvent
    extra = 0
    readonly_fields = ("event_type", "note", "payload", "created_at")


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "payment", "status", "amount_rub", "reason", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("=id", "public_id", "=order__id", "=payment__id", "reason")
    readonly_fields = ("public_id", "provider_reference", "idempotency_key", "processed_at", "created_at", "updated_at")
    inlines = [RefundItemInline, RefundEventInline]
    actions = ["process_selected_refunds"]

    @admin.action(description="Process selected refunds")
    def process_selected_refunds(self, request, queryset):
        if not request.user.has_perm("refunds.process_refund") and not request.user.is_superuser:
            self.message_user(request, "Недостаточно прав для проведения возврата.", messages.ERROR)
            return
        succeeded = 0
        failed = 0
        for refund in queryset:
            try:
                process_refund(refund)
                succeeded += 1
            except ValidationError:
                failed += 1
        level = messages.SUCCESS if not failed else messages.WARNING
        self.message_user(request, f"Проведено: {succeeded}; с ошибкой: {failed}.", level)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "claim_type", "status", "customer_name", "created_at")
    list_filter = ("status", "claim_type", "created_at")
    search_fields = ("=id", "=order__id", "customer_name", "contact", "description")

    def get_list_display(self, request):
        if request.user.has_perm("refunds.view_claim_pii") or request.user.is_superuser:
            return super().get_list_display(request)
        return ("id", "order", "claim_type", "status", "masked_customer", "created_at")

    def get_search_fields(self, request):
        if request.user.has_perm("refunds.view_claim_pii") or request.user.is_superuser:
            return super().get_search_fields(request)
        return ("=id", "=order__id")

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or [])
        if not request.user.has_perm("refunds.view_claim_pii") and not request.user.is_superuser:
            excluded.extend(["customer_name", "contact", "description"])
        return excluded

    @admin.display(description="customer")
    def masked_customer(self, obj):
        return f"Клиент претензии #{obj.pk}"
