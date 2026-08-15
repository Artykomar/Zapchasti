from django.contrib import admin

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
    readonly_fields = ("public_id", "bank_order_id", "form_url", "idempotency_key", "paid_at", "created_at", "updated_at")
    inlines = [PaymentAttemptInline, PaymentEventInline]


@admin.register(PaymentProviderCredentialRef)
class PaymentProviderCredentialRefAdmin(admin.ModelAdmin):
    list_display = ("provider", "mode", "credential_ref", "is_active", "updated_at")
    list_filter = ("provider", "mode", "is_active")
    search_fields = ("provider", "mode", "credential_ref")
