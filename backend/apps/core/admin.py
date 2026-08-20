from django.contrib import admin

from .models import LegalDocument, LegalEntitySettings, RetentionPolicy, SiteSettings


class SingletonAdminMixin:
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Brand and domain", {"fields": ("brand_name", "tagline", "site_url", "canonical_domain")}),
        ("Contacts", {"fields": ("region", "address", "business_hours", "public_phone_label", "public_phone_href", "public_email", "max_url", "max_label")}),
        ("Documents", {"fields": ("privacy_policy_version", "privacy_consent_version", "terms_version", "bank_review_mode")}),
    )
    list_display = ("brand_name", "site_url", "public_phone_label", "public_email", "updated_at")


@admin.register(LegalEntitySettings)
class LegalEntitySettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Seller profile", {"fields": ("seller_profile", "display_name", "legal_name", "is_ready_for_production")}),
        ("Registration", {"fields": ("inn", "ogrn", "kpp", "legal_address", "actual_address", "claims_email")}),
        ("Bank and taxes", {"fields": ("bank_name", "bank_account", "correspondent_account", "bik", "tax_mode", "vat_label")}),
    )
    list_display = ("public_name", "seller_profile", "inn", "tax_mode", "is_ready_for_production", "updated_at")


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "version", "is_published", "published_at", "updated_at")
    list_filter = ("kind", "is_published", "published_at")
    search_fields = ("title", "version", "body")


@admin.register(RetentionPolicy)
class RetentionPolicyAdmin(SingletonAdminMixin, admin.ModelAdmin):
    list_display = (
        "request_retention_days",
        "cancelled_order_retention_days",
        "notification_retention_days",
        "audit_retention_days",
        "updated_at",
    )
