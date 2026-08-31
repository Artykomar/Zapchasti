from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.security)
def cdek_configuration_checks(app_configs, **kwargs):
    errors = []
    if settings.CDEK_MODE not in {"test", "prod"}:
        errors.append(Error("CDEK_MODE must be test or prod.", id="warehouse.E001"))
    if settings.CDEK_ENABLED:
        required = ["CDEK_CLIENT_ID", "CDEK_CLIENT_SECRET", "CDEK_SENDER_NAME", "CDEK_SENDER_PHONE", "CDEK_SENDER_ADDRESS"]
        if any(not str(getattr(settings, key, "")).strip() for key in required) or settings.CDEK_SENDER_CITY_CODE <= 0:
            errors.append(Error("Enabled CDEK requires credentials and a complete sender profile.", id="warehouse.E002"))
    return errors
