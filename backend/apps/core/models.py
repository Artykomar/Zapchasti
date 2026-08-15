from django.db import models


class SingletonModel(models.Model):
    singleton_id = models.PositiveSmallIntegerField(default=1, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.first() or cls()


class SiteSettings(SingletonModel):
    brand_name = models.CharField(max_length=120, default="Zemazap")
    tagline = models.CharField(max_length=180, default="автозапчасти под заказ")
    site_url = models.URLField(default="http://127.0.0.1:3000")
    canonical_domain = models.CharField(max_length=180, blank=True)
    region = models.CharField(max_length=180, default="Регион работы уточняется")
    address = models.TextField(blank=True)
    business_hours = models.CharField(max_length=180, default="Пн-Сб, график будет задан")
    public_phone_label = models.CharField(max_length=80, default="+7 (000) 000-00-00")
    public_phone_href = models.CharField(max_length=40, default="+70000000000")
    public_email = models.EmailField(default="orders@example.ru")
    max_url = models.URLField(blank=True)
    max_label = models.CharField(max_length=120, default="MAX")
    privacy_policy_version = models.CharField(max_length=80, default="draft-2026-08-15")
    privacy_consent_version = models.CharField(max_length=80, default="draft-2026-08-15")
    terms_version = models.CharField(max_length=80, default="draft-2026-08-15")
    bank_review_mode = models.BooleanField(default=True)

    class Meta:
        verbose_name = "site settings"
        verbose_name_plural = "site settings"

    def __str__(self) -> str:
        return self.brand_name


class LegalEntitySettings(SingletonModel):
    class SellerProfile(models.TextChoices):
        UNKNOWN = "unknown", "unknown"
        IP = "ip", "IP"
        OOO = "ooo", "OOO"

    class TaxMode(models.TextChoices):
        UNKNOWN = "unknown", "unknown"
        USN_INCOME = "usn_income", "USN income"
        USN_INCOME_EXPENSE = "usn_income_expense", "USN income-expense"
        OSN = "osn", "OSN"
        PATENT = "patent", "patent"

    seller_profile = models.CharField(
        max_length=20,
        choices=SellerProfile.choices,
        default=SellerProfile.UNKNOWN,
    )
    display_name = models.CharField(max_length=240, blank=True)
    legal_name = models.CharField(max_length=240, blank=True)
    inn = models.CharField(max_length=12, blank=True)
    ogrn = models.CharField(max_length=15, blank=True)
    kpp = models.CharField(max_length=9, blank=True)
    legal_address = models.TextField(blank=True)
    actual_address = models.TextField(blank=True)
    claims_email = models.EmailField(blank=True)
    bank_name = models.CharField(max_length=240, blank=True)
    bank_account = models.CharField(max_length=40, blank=True)
    correspondent_account = models.CharField(max_length=40, blank=True)
    bik = models.CharField(max_length=12, blank=True)
    tax_mode = models.CharField(max_length=40, choices=TaxMode.choices, default=TaxMode.UNKNOWN)
    vat_label = models.CharField(max_length=80, default="НДС не задан")
    is_ready_for_production = models.BooleanField(default=False)

    class Meta:
        verbose_name = "legal entity settings"
        verbose_name_plural = "legal entity settings"

    def __str__(self) -> str:
        return self.display_name or self.legal_name or self.seller_profile

    @property
    def public_name(self) -> str:
        return self.display_name or self.legal_name or "Реквизиты продавца не заполнены"
