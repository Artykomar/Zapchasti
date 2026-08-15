from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from .models import LegalEntitySettings, SiteSettings


@dataclass(frozen=True)
class LaunchFeatureFlags:
    payments_enabled: bool
    payments_provider: str
    payments_mode: str
    fiscalization_enabled: bool
    max_enabled: bool
    pii_in_notifications_allowed: bool
    analytics_enabled: bool
    indexing_allowed: bool


def _safe_singleton(model_class):
    try:
        return model_class.load()
    except (OperationalError, ProgrammingError):
        return model_class()


def get_site_settings() -> SiteSettings:
    site_settings = _safe_singleton(SiteSettings)
    site_settings.brand_name = getattr(settings, "ZEMAZAP_BRAND_NAME", site_settings.brand_name)
    site_settings.tagline = getattr(settings, "ZEMAZAP_TAGLINE", site_settings.tagline)
    site_settings.site_url = getattr(settings, "ZEMAZAP_SITE_URL", site_settings.site_url)
    site_settings.region = getattr(settings, "ZEMAZAP_REGION", site_settings.region)
    site_settings.address = getattr(settings, "ZEMAZAP_ADDRESS", site_settings.address)
    site_settings.business_hours = getattr(settings, "ZEMAZAP_BUSINESS_HOURS", site_settings.business_hours)
    site_settings.public_phone_label = getattr(
        settings, "ZEMAZAP_PUBLIC_PHONE_LABEL", site_settings.public_phone_label
    )
    site_settings.public_phone_href = getattr(
        settings, "ZEMAZAP_PUBLIC_PHONE_HREF", site_settings.public_phone_href
    )
    site_settings.public_email = getattr(settings, "ZEMAZAP_PUBLIC_EMAIL", site_settings.public_email)
    site_settings.max_url = getattr(settings, "ZEMAZAP_MAX_URL", site_settings.max_url)
    site_settings.privacy_policy_version = getattr(
        settings, "ZEMAZAP_PRIVACY_POLICY_VERSION", site_settings.privacy_policy_version
    )
    site_settings.privacy_consent_version = getattr(
        settings, "ZEMAZAP_PRIVACY_CONSENT_VERSION", site_settings.privacy_consent_version
    )
    site_settings.terms_version = getattr(settings, "ZEMAZAP_TERMS_VERSION", site_settings.terms_version)
    return site_settings


def get_legal_entity_settings() -> LegalEntitySettings:
    legal_settings = _safe_singleton(LegalEntitySettings)
    legal_settings.seller_profile = getattr(
        settings, "ZEMAZAP_SELLER_PROFILE", legal_settings.seller_profile
    )
    legal_settings.legal_name = getattr(settings, "ZEMAZAP_LEGAL_NAME", legal_settings.legal_name)
    legal_settings.inn = getattr(settings, "ZEMAZAP_LEGAL_INN", legal_settings.inn)
    legal_settings.ogrn = getattr(settings, "ZEMAZAP_LEGAL_OGRN", legal_settings.ogrn)
    legal_settings.kpp = getattr(settings, "ZEMAZAP_LEGAL_KPP", legal_settings.kpp)
    legal_settings.legal_address = getattr(settings, "ZEMAZAP_LEGAL_ADDRESS", legal_settings.legal_address)
    legal_settings.actual_address = getattr(settings, "ZEMAZAP_ACTUAL_ADDRESS", legal_settings.actual_address)
    legal_settings.claims_email = getattr(settings, "ZEMAZAP_CLAIMS_EMAIL", legal_settings.claims_email)
    legal_settings.bank_name = getattr(settings, "ZEMAZAP_BANK_NAME", legal_settings.bank_name)
    legal_settings.bank_account = getattr(settings, "ZEMAZAP_BANK_ACCOUNT", legal_settings.bank_account)
    legal_settings.correspondent_account = getattr(
        settings, "ZEMAZAP_BANK_CORRESPONDENT_ACCOUNT", legal_settings.correspondent_account
    )
    legal_settings.bik = getattr(settings, "ZEMAZAP_BANK_BIK", legal_settings.bik)
    legal_settings.tax_mode = getattr(settings, "ZEMAZAP_TAX_MODE", legal_settings.tax_mode)
    legal_settings.vat_label = getattr(settings, "ZEMAZAP_VAT_LABEL", legal_settings.vat_label)
    return legal_settings


def get_launch_feature_flags() -> LaunchFeatureFlags:
    return LaunchFeatureFlags(
        payments_enabled=getattr(settings, "PAYMENTS_ENABLED", False),
        payments_provider=getattr(settings, "PAYMENTS_PROVIDER", "alfa"),
        payments_mode=getattr(settings, "PAYMENTS_MODE", "test"),
        fiscalization_enabled=getattr(settings, "FISCALIZATION_ENABLED", False),
        max_enabled=getattr(settings, "MAX_ENABLED", False),
        pii_in_notifications_allowed=getattr(settings, "PII_IN_NOTIFICATIONS_ALLOWED", False),
        analytics_enabled=getattr(settings, "ANALYTICS_ENABLED", False),
        indexing_allowed=getattr(settings, "ZEMAZAP_INDEXING_ALLOWED", False),
    )


def build_public_site_settings() -> dict:
    site_settings = get_site_settings()
    legal_settings = get_legal_entity_settings()
    feature_flags = get_launch_feature_flags()

    return {
        "brand": {
            "name": site_settings.brand_name,
            "tagline": site_settings.tagline,
            "siteUrl": site_settings.site_url,
            "canonicalDomain": site_settings.canonical_domain,
        },
        "contacts": {
            "region": site_settings.region,
            "address": site_settings.address,
            "businessHours": site_settings.business_hours,
            "phoneLabel": site_settings.public_phone_label,
            "phoneHref": site_settings.public_phone_href,
            "email": site_settings.public_email,
            "maxUrl": site_settings.max_url if feature_flags.max_enabled else "",
            "maxLabel": site_settings.max_label,
        },
        "legal": {
            "sellerProfile": legal_settings.seller_profile,
            "publicName": legal_settings.public_name,
            "legalName": legal_settings.legal_name,
            "inn": legal_settings.inn,
            "ogrn": legal_settings.ogrn,
            "kpp": legal_settings.kpp,
            "legalAddress": legal_settings.legal_address,
            "actualAddress": legal_settings.actual_address,
            "claimsEmail": legal_settings.claims_email,
            "taxMode": legal_settings.tax_mode,
            "vatLabel": legal_settings.vat_label,
            "isReadyForProduction": legal_settings.is_ready_for_production,
        },
        "documents": {
            "privacyPolicyVersion": site_settings.privacy_policy_version,
            "privacyConsentVersion": site_settings.privacy_consent_version,
            "termsVersion": site_settings.terms_version,
            "bankReviewMode": site_settings.bank_review_mode,
        },
        "featureFlags": {
            "paymentsEnabled": feature_flags.payments_enabled,
            "paymentsProvider": feature_flags.payments_provider,
            "paymentsMode": feature_flags.payments_mode,
            "fiscalizationEnabled": feature_flags.fiscalization_enabled,
            "maxEnabled": feature_flags.max_enabled,
            "piiInNotificationsAllowed": feature_flags.pii_in_notifications_allowed,
            "analyticsEnabled": feature_flags.analytics_enabled,
            "indexingAllowed": feature_flags.indexing_allowed,
        },
    }
