from __future__ import annotations

from django.conf import settings
from django.core.checks import Error, Tags, Warning, register


VALID_PAYMENT_MODES = {"test", "prod"}
VALID_PAYMENT_PROVIDERS = {"alfa", "mock"}
VALID_FISCAL_PROVIDERS = {"alfa", "mock"}
PLACEHOLDER_MARKERS = (
    "example",
    "draft",
    "unknown",
    "уточняется",
    "будет задан",
    "+7 (000)",
    "+7000",
    "ндс не задан",
)


def _is_local_url(value: str) -> bool:
    return "127.0.0.1" in value or "localhost" in value or value.startswith("http://")


def _missing_setting(name: str) -> bool:
    return not str(getattr(settings, name, "")).strip()


def _placeholder_setting(name: str) -> bool:
    value = str(getattr(settings, name, "")).strip().lower()
    return not value or any(marker in value for marker in PLACEHOLDER_MARKERS)


@register(Tags.security)
def launch_configuration_checks(app_configs, **kwargs):
    messages = []

    payments_mode = getattr(settings, "PAYMENTS_MODE", "test")
    payments_provider = getattr(settings, "PAYMENTS_PROVIDER", "alfa")
    payments_enabled = getattr(settings, "PAYMENTS_ENABLED", False)
    fiscalization_enabled = getattr(settings, "FISCALIZATION_ENABLED", False)
    fiscal_provider = getattr(settings, "FISCAL_PROVIDER", "mock")

    if payments_mode not in VALID_PAYMENT_MODES:
        messages.append(
            Error(
                "PAYMENTS_MODE must be either 'test' or 'prod'.",
                id="zemazap.E001",
            )
        )

    if payments_provider not in VALID_PAYMENT_PROVIDERS:
        messages.append(
            Error(
                "PAYMENTS_PROVIDER must be either 'alfa' or 'mock'.",
                id="zemazap.E002",
            )
        )

    if fiscal_provider not in VALID_FISCAL_PROVIDERS:
        messages.append(Error("FISCAL_PROVIDER must be either 'alfa' or 'mock'.", id="zemazap.E008"))

    if payments_enabled and getattr(settings, "ZEMAZAP_SELLER_PROFILE", "unknown") == "unknown":
        messages.append(
            Error(
                "Payments cannot be enabled while ZEMAZAP_SELLER_PROFILE is unknown.",
                id="zemazap.E003",
            )
        )

    if payments_enabled and payments_mode == "prod" and not fiscalization_enabled:
        messages.append(
            Error(
                "Production payments require FISCALIZATION_ENABLED=true.",
                id="zemazap.E004",
            )
        )

    if payments_enabled and payments_mode == "prod" and payments_provider == "mock":
        messages.append(Error("Mock payment provider is forbidden in production mode.", id="zemazap.E009"))

    if payments_enabled and payments_mode == "prod" and fiscal_provider == "mock":
        messages.append(Error("Mock fiscal provider is forbidden with production payments.", id="zemazap.E010"))

    if payments_enabled and payments_mode == "prod" and payments_provider == "alfa":
        for setting_name in ("ALFA_BANK_GATEWAY_URL", "ALFA_BANK_CALLBACK_TOKEN"):
            if _missing_setting(setting_name):
                messages.append(
                    Error(
                        f"{setting_name} is required for production Alfa-Bank payments.",
                        id="zemazap.E005",
                    )
                )
        has_token = not _missing_setting("ALFA_BANK_TOKEN")
        has_login_password = not _missing_setting("ALFA_BANK_USERNAME") and not _missing_setting("ALFA_BANK_PASSWORD")
        if not has_token and not has_login_password:
            messages.append(
                Error(
                    "Production Alfa-Bank payments require ALFA_BANK_TOKEN or username/password credentials.",
                    id="zemazap.E005",
                )
            )
        gateway_url = str(getattr(settings, "ALFA_BANK_GATEWAY_URL", "")).strip()
        if gateway_url and not gateway_url.startswith("https://"):
            messages.append(Error("ALFA_BANK_GATEWAY_URL must use HTTPS.", id="zemazap.E014"))
        callback_token = str(getattr(settings, "ALFA_BANK_CALLBACK_TOKEN", ""))
        if callback_token and len(callback_token) < 32:
            messages.append(Error("ALFA_BANK_CALLBACK_TOKEN must be at least 32 characters.", id="zemazap.E015"))
        if fiscal_provider == "alfa" and _missing_setting("FISCAL_TAX_SYSTEM"):
            messages.append(Error("FISCAL_TAX_SYSTEM is required for Alfa fiscalization.", id="zemazap.E016"))

    if getattr(settings, "ZEMAZAP_TELEGRAM_BOT_TOKEN", "") and not getattr(
        settings, "PII_IN_NOTIFICATIONS_ALLOWED", False
    ):
        messages.append(
            Warning(
                "Telegram is configured while PII_IN_NOTIFICATIONS_ALLOWED=false; notifications must stay PII-safe.",
                id="zemazap.W001",
            )
        )

    return messages


@register(Tags.security, deploy=True)
def production_launch_configuration_checks(app_configs, **kwargs):
    messages = []

    database_engine = settings.DATABASES["default"]["ENGINE"]
    if database_engine != "django.db.backends.postgresql":
        messages.append(
            Error(
                "Production deployment requires PostgreSQL through DATABASE_URL.",
                id="zemazap.E012",
            )
        )

    if getattr(settings, "STORAGE_BACKEND", "local") != "yandex":
        messages.append(
            Error(
                "Production deployment requires STORAGE_BACKEND=yandex for durable media storage.",
                id="zemazap.E013",
            )
        )

    if _is_local_url(getattr(settings, "ZEMAZAP_SITE_URL", "")):
        messages.append(
            Error(
                "ZEMAZAP_SITE_URL must be the real HTTPS production URL for deployment.",
                id="zemazap.E006",
            )
        )

    for setting_name in (
        "ZEMAZAP_PUBLIC_PHONE_LABEL",
        "ZEMAZAP_PUBLIC_PHONE_HREF",
        "ZEMAZAP_PUBLIC_EMAIL",
        "ZEMAZAP_REGION",
        "ZEMAZAP_ADDRESS",
        "ZEMAZAP_BUSINESS_HOURS",
        "ZEMAZAP_SELLER_PROFILE",
        "ZEMAZAP_LEGAL_NAME",
        "ZEMAZAP_LEGAL_INN",
        "ZEMAZAP_LEGAL_OGRN",
        "ZEMAZAP_LEGAL_ADDRESS",
        "ZEMAZAP_ACTUAL_ADDRESS",
        "ZEMAZAP_CLAIMS_EMAIL",
        "ZEMAZAP_PRIVACY_POLICY_VERSION",
        "ZEMAZAP_PRIVACY_CONSENT_VERSION",
        "ZEMAZAP_TERMS_VERSION",
        "ZEMAZAP_TAX_MODE",
        "ZEMAZAP_VAT_LABEL",
    ):
        if _placeholder_setting(setting_name):
            messages.append(
                Error(
                    f"{setting_name} must contain a non-placeholder deployment value.",
                    id="zemazap.E007",
                )
            )

    if getattr(settings, "STORAGE_BACKEND", "local") == "yandex":
        for setting_name in (
            "YANDEX_OBJECT_STORAGE_BUCKET",
            "YANDEX_OBJECT_STORAGE_ACCESS_KEY_ID",
            "YANDEX_OBJECT_STORAGE_SECRET_ACCESS_KEY",
        ):
            if _missing_setting(setting_name):
                messages.append(
                    Error(f"{setting_name} is required for Yandex Object Storage.", id="zemazap.E011")
                )

    return messages
