from django.contrib import admin, messages

from django.core.exceptions import ValidationError

from .services import synchronize_payment_status

from .models import Payment, PaymentAttempt, PaymentEvent, PaymentProviderCredentialRef


class PaymentEventInline(admin.TabularInline):
    model = PaymentEvent
    extra = 0
    readonly_fields = ("created_at",)


class PaymentAttemptInline(admin.TabularInline):
    model = PaymentAttempt
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "provider", "mode", "status", "amount_rub", "currency", "created_at")
    list_filter = ("provider", "mode", "status", "created_at")
    search_fields = ("=id", "public_id", "bank_order_id", "=order__id", "order__customer_name")
    readonly_fields = ("public_id", "bank_order_id", "provider_order_number", "form_url", "idempotency_key", "paid_at", "created_at", "updated_at")
    inlines = [PaymentAttemptInline, PaymentEventInline]
    actions = ["refresh_provider_status"]

    def get_search_fields(self, request):
        if request.user.has_perm("payments.view_payment_details") or request.user.is_superuser:
            return super().get_search_fields(request)
        return ("=id", "public_id", "=order__id")

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or [])
        if not request.user.has_perm("payments.view_payment_details") and not request.user.is_superuser:
            excluded.extend(
                ["bank_order_id", "provider_order_number", "form_url", "idempotency_key", "failure_reason"]
            )
        return excluded

    def get_inlines(self, request, obj):
        if request.user.has_perm("payments.view_payment_details") or request.user.is_superuser:
            return super().get_inlines(request, obj)
        return []

    @admin.action(description="Check selected payment status at provider")
    def refresh_provider_status(self, request, queryset):
        updated = 0
        failed = 0
        for payment in queryset:
            try:
                synchronize_payment_status(payment)
                updated += 1
            except ValidationError:
                failed += 1
        level = messages.SUCCESS if not failed else messages.WARNING
        self.message_user(request, f"Проверено: {updated}; с ошибкой: {failed}.", level)


@admin.register(PaymentProviderCredentialRef)
class PaymentProviderCredentialRefAdmin(admin.ModelAdmin):
    list_display = ("provider", "mode", "credential_ref", "is_active", "updated_at")
    list_filter = ("provider", "mode", "is_active")
    search_fields = ("provider", "mode", "credential_ref")
