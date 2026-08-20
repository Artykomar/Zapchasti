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


class LegalDocument(models.Model):
    class Kind(models.TextChoices):
        PRIVACY_POLICY = "privacy_policy", "Политика персональных данных"
        PRIVACY_CONSENT = "privacy_consent", "Согласие на обработку ПДн"
        TERMS = "terms", "Условия заказа"
        DELIVERY = "delivery", "Доставка"
        PAYMENT = "payment", "Оплата"
        WARRANTY = "warranty", "Гарантия"
        RETURNS = "returns", "Возврат"

    kind = models.CharField(max_length=40, choices=Kind.choices)
    version = models.CharField(max_length=80)
    title = models.CharField(max_length=240)
    body = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "-published_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["kind", "version"], name="unique_legal_document_version")
        ]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} — {self.version}"


class RetentionPolicy(SingletonModel):
    request_retention_days = models.PositiveIntegerField(default=1095)
    cancelled_order_retention_days = models.PositiveIntegerField(default=1095)
    notification_retention_days = models.PositiveIntegerField(default=365)
    audit_retention_days = models.PositiveIntegerField(default=1095)
    anonymize_test_data_after_days = models.PositiveIntegerField(default=30)

    class Meta:
        verbose_name = "retention policy"
        verbose_name_plural = "retention policy"

    def __str__(self) -> str:
        return "Политика хранения данных"
