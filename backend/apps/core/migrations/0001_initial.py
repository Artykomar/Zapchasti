# Generated manually for the Zemazap launch-readiness foundation.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LegalEntitySettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("singleton_id", models.PositiveSmallIntegerField(default=1, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("seller_profile", models.CharField(choices=[("unknown", "unknown"), ("ip", "IP"), ("ooo", "OOO")], default="unknown", max_length=20)),
                ("display_name", models.CharField(blank=True, max_length=240)),
                ("legal_name", models.CharField(blank=True, max_length=240)),
                ("inn", models.CharField(blank=True, max_length=12)),
                ("ogrn", models.CharField(blank=True, max_length=15)),
                ("kpp", models.CharField(blank=True, max_length=9)),
                ("legal_address", models.TextField(blank=True)),
                ("actual_address", models.TextField(blank=True)),
                ("claims_email", models.EmailField(blank=True, max_length=254)),
                ("bank_name", models.CharField(blank=True, max_length=240)),
                ("bank_account", models.CharField(blank=True, max_length=40)),
                ("correspondent_account", models.CharField(blank=True, max_length=40)),
                ("bik", models.CharField(blank=True, max_length=12)),
                ("tax_mode", models.CharField(choices=[("unknown", "unknown"), ("usn_income", "USN income"), ("usn_income_expense", "USN income-expense"), ("osn", "OSN"), ("patent", "patent")], default="unknown", max_length=40)),
                ("vat_label", models.CharField(default="НДС не задан", max_length=80)),
                ("is_ready_for_production", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "legal entity settings",
                "verbose_name_plural": "legal entity settings",
            },
        ),
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("singleton_id", models.PositiveSmallIntegerField(default=1, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("brand_name", models.CharField(default="Zemazap", max_length=120)),
                ("tagline", models.CharField(default="автозапчасти под заказ", max_length=180)),
                ("site_url", models.URLField(default="http://127.0.0.1:3000")),
                ("canonical_domain", models.CharField(blank=True, max_length=180)),
                ("region", models.CharField(default="Регион работы уточняется", max_length=180)),
                ("address", models.TextField(blank=True)),
                ("business_hours", models.CharField(default="Пн-Сб, график будет задан", max_length=180)),
                ("public_phone_label", models.CharField(default="+7 (000) 000-00-00", max_length=80)),
                ("public_phone_href", models.CharField(default="+70000000000", max_length=40)),
                ("public_email", models.EmailField(default="orders@example.ru", max_length=254)),
                ("max_url", models.URLField(blank=True)),
                ("max_label", models.CharField(default="MAX", max_length=120)),
                ("privacy_policy_version", models.CharField(default="draft-2026-08-15", max_length=80)),
                ("privacy_consent_version", models.CharField(default="draft-2026-08-15", max_length=80)),
                ("terms_version", models.CharField(default="draft-2026-08-15", max_length=80)),
                ("bank_review_mode", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "site settings",
                "verbose_name_plural": "site settings",
            },
        ),
    ]
