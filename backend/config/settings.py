import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be an integer.") from exc


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"{name} is required when DJANGO_DEBUG=false.")
    return value


DEBUG = env_bool("DJANGO_DEBUG", True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-zemazap-local-dev-only"
    else:
        SECRET_KEY = required_env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost" if DEBUG else "")
if not DEBUG and not ALLOWED_HOSTS:
    required_env("DJANGO_ALLOWED_HOSTS")

CORS_ALLOWED_ORIGINS = env_list("DJANGO_CORS_ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", ",".join(CORS_ALLOWED_ORIGINS))


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "apps.core",
    "apps.catalog",
    "apps.customers",
    "apps.leads",
    "apps.imports",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'zemazap_django.sqlite3'}")
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=60, ssl_require=False)
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = env_int("DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE", 512 * 1024)
FILE_UPLOAD_MAX_MEMORY_SIZE = env_int("DJANGO_FILE_UPLOAD_MAX_MEMORY_SIZE", 5 * 1024 * 1024)

SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SECURE_HSTS_SECONDS = env_int("DJANGO_SECURE_HSTS_SECONDS", 0 if DEBUG else 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", not DEBUG)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"

ZEMAZAP_BRAND_NAME = os.getenv("ZEMAZAP_BRAND_NAME", "Zemazap")
ZEMAZAP_TAGLINE = os.getenv("ZEMAZAP_TAGLINE", "автозапчасти под заказ")
ZEMAZAP_SITE_URL = os.getenv("ZEMAZAP_SITE_URL", "http://127.0.0.1:3000")
ZEMAZAP_INDEXING_ALLOWED = env_bool("ZEMAZAP_INDEXING_ALLOWED", False)
ZEMAZAP_REGION = os.getenv("ZEMAZAP_REGION", "Регион работы уточняется")
ZEMAZAP_ADDRESS = os.getenv("ZEMAZAP_ADDRESS", "")
ZEMAZAP_BUSINESS_HOURS = os.getenv("ZEMAZAP_BUSINESS_HOURS", "Пн-Сб, график будет задан")
ZEMAZAP_PUBLIC_PHONE_LABEL = os.getenv("ZEMAZAP_PUBLIC_PHONE_LABEL", "+7 (000) 000-00-00")
ZEMAZAP_PUBLIC_PHONE_HREF = os.getenv("ZEMAZAP_PUBLIC_PHONE_HREF", "+70000000000")
ZEMAZAP_PUBLIC_EMAIL = os.getenv("ZEMAZAP_PUBLIC_EMAIL", "orders@example.ru")
ZEMAZAP_MAX_URL = os.getenv("ZEMAZAP_MAX_URL", "")
ZEMAZAP_SELLER_PROFILE = os.getenv("ZEMAZAP_SELLER_PROFILE", "unknown").strip().lower()
ZEMAZAP_LEGAL_NAME = os.getenv("ZEMAZAP_LEGAL_NAME", "")
ZEMAZAP_LEGAL_INN = os.getenv("ZEMAZAP_LEGAL_INN", "")
ZEMAZAP_LEGAL_OGRN = os.getenv("ZEMAZAP_LEGAL_OGRN", "")
ZEMAZAP_LEGAL_KPP = os.getenv("ZEMAZAP_LEGAL_KPP", "")
ZEMAZAP_LEGAL_ADDRESS = os.getenv("ZEMAZAP_LEGAL_ADDRESS", "")
ZEMAZAP_ACTUAL_ADDRESS = os.getenv("ZEMAZAP_ACTUAL_ADDRESS", "")
ZEMAZAP_CLAIMS_EMAIL = os.getenv("ZEMAZAP_CLAIMS_EMAIL", ZEMAZAP_PUBLIC_EMAIL)
ZEMAZAP_BANK_NAME = os.getenv("ZEMAZAP_BANK_NAME", "")
ZEMAZAP_BANK_ACCOUNT = os.getenv("ZEMAZAP_BANK_ACCOUNT", "")
ZEMAZAP_BANK_CORRESPONDENT_ACCOUNT = os.getenv("ZEMAZAP_BANK_CORRESPONDENT_ACCOUNT", "")
ZEMAZAP_BANK_BIK = os.getenv("ZEMAZAP_BANK_BIK", "")
ZEMAZAP_TAX_MODE = os.getenv("ZEMAZAP_TAX_MODE", "unknown").strip().lower()
ZEMAZAP_VAT_LABEL = os.getenv("ZEMAZAP_VAT_LABEL", "НДС не задан")
ZEMAZAP_PRIVACY_POLICY_VERSION = os.getenv("ZEMAZAP_PRIVACY_POLICY_VERSION", "draft-2026-08-15")
ZEMAZAP_PRIVACY_CONSENT_VERSION = os.getenv("ZEMAZAP_PRIVACY_CONSENT_VERSION", "draft-2026-08-15")
ZEMAZAP_TERMS_VERSION = os.getenv("ZEMAZAP_TERMS_VERSION", "draft-2026-08-15")

PAYMENTS_ENABLED = env_bool("PAYMENTS_ENABLED", False)
PAYMENTS_PROVIDER = os.getenv("PAYMENTS_PROVIDER", "alfa").strip().lower()
PAYMENTS_MODE = os.getenv("PAYMENTS_MODE", "test").strip().lower()
FISCALIZATION_ENABLED = env_bool("FISCALIZATION_ENABLED", False)
MAX_ENABLED = env_bool("MAX_ENABLED", False)
PII_IN_NOTIFICATIONS_ALLOWED = env_bool("PII_IN_NOTIFICATIONS_ALLOWED", False)
ANALYTICS_ENABLED = env_bool("ANALYTICS_ENABLED", False)

ALFA_BANK_GATEWAY_URL = os.getenv("ALFA_BANK_GATEWAY_URL", "")
ALFA_BANK_USERNAME = os.getenv("ALFA_BANK_USERNAME", "")
ALFA_BANK_PASSWORD = os.getenv("ALFA_BANK_PASSWORD", "")

YANDEX_OBJECT_STORAGE_ENDPOINT = os.getenv("YANDEX_OBJECT_STORAGE_ENDPOINT", "")
YANDEX_OBJECT_STORAGE_BUCKET = os.getenv("YANDEX_OBJECT_STORAGE_BUCKET", "")
YANDEX_OBJECT_STORAGE_REGION = os.getenv("YANDEX_OBJECT_STORAGE_REGION", "ru-central1")
YANDEX_OBJECT_STORAGE_ACCESS_KEY_ID = os.getenv("YANDEX_OBJECT_STORAGE_ACCESS_KEY_ID", "")
YANDEX_OBJECT_STORAGE_SECRET_ACCESS_KEY = os.getenv("YANDEX_OBJECT_STORAGE_SECRET_ACCESS_KEY", "")

ZEMAZAP_MANAGER_EMAIL = os.getenv("ZEMAZAP_MANAGER_EMAIL", "")
ZEMAZAP_TELEGRAM_CHAT_ID = os.getenv("ZEMAZAP_TELEGRAM_CHAT_ID", "")
ZEMAZAP_TELEGRAM_BOT_TOKEN = os.getenv("ZEMAZAP_TELEGRAM_BOT_TOKEN", "")

EMAIL_HOST = os.getenv("ZEMAZAP_SMTP_HOST", "")
EMAIL_PORT = int(os.getenv("ZEMAZAP_SMTP_PORT", "465"))
EMAIL_HOST_USER = os.getenv("ZEMAZAP_SMTP_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("ZEMAZAP_SMTP_PASSWORD", "")
EMAIL_USE_SSL = os.getenv("ZEMAZAP_SMTP_SECURE", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("ZEMAZAP_SMTP_FROM", EMAIL_HOST_USER or "noreply@zemazap.local")

REST_RENDERER_CLASSES = ["rest_framework.renderers.JSONRenderer"]
if DEBUG:
    REST_RENDERER_CLASSES.append("rest_framework.renderers.BrowsableAPIRenderer")

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": REST_RENDERER_CLASSES,
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/min",
        "user": "600/min",
        "customer_requests": os.getenv("DJANGO_CUSTOMER_REQUEST_THROTTLE", "10/min"),
    },
}
