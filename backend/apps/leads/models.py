from django.db import models


class CustomerRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "new"
        IN_WORK = "in_work", "in work"
        WAITING_CUSTOMER = "waiting_customer", "waiting customer"
        DONE = "done", "done"
        CANCELLED = "cancelled", "cancelled"

    class Source(models.TextChoices):
        CART = "cart", "cart"
        REQUEST_FORM = "request_form", "request form"

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
    )
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.NEW)
    source = models.CharField(max_length=40, choices=Source.choices)
    customer_name = models.CharField(max_length=160)
    contact = models.CharField(max_length=160)
    vehicle = models.CharField(max_length=240, blank=True)
    request_text = models.TextField(blank=True)
    privacy_accepted = models.BooleanField(default=False)
    privacy_policy_version = models.CharField(max_length=80, default="draft-2026-08-15")
    privacy_consent_version = models.CharField(max_length=80, default="draft-2026-08-15")
    consent_accepted_at = models.DateTimeField(null=True, blank=True)
    consent_source = models.CharField(max_length=120, blank=True)
    consent_ip = models.GenericIPAddressField(null=True, blank=True)
    consent_user_agent = models.CharField(max_length=300, blank=True)
    total_estimate_rub = models.PositiveIntegerField(default=0)
    anonymized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]
        permissions = [
            ("view_request_pii", "Can view personal data in requests"),
            ("export_request_pii", "Can export personal data from requests"),
            ("anonymize_request_pii", "Can anonymize personal data in requests"),
        ]

    def __str__(self) -> str:
        return f"{self.customer_name} - {self.status}"


class CustomerRequestItem(models.Model):
    request = models.ForeignKey(CustomerRequest, on_delete=models.CASCADE, related_name="items")
    part = models.ForeignKey(
        "catalog.Part",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_items",
    )
    part_name = models.CharField(max_length=240)
    article = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_snapshot_rub = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.part_name} x {self.quantity}"


class CustomerRequestEvent(models.Model):
    request = models.ForeignKey(CustomerRequest, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=80)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["request", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} at {self.created_at:%Y-%m-%d %H:%M}"

# Create your models here.
