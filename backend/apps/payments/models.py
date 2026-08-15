from __future__ import annotations

import uuid

from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "draft"
        PENDING = "pending", "pending"
        SUCCEEDED = "succeeded", "succeeded"
        FAILED = "failed", "failed"
        CANCELLED = "cancelled", "cancelled"
        REFUNDED = "refunded", "refunded"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="payments")
    provider = models.CharField(max_length=40, default="alfa")
    mode = models.CharField(max_length=20, default="test")
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.DRAFT)
    amount_rub = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="RUB")
    bank_order_id = models.CharField(max_length=120, blank=True)
    form_url = models.URLField(blank=True)
    idempotency_key = models.CharField(max_length=160, unique=True)
    failure_reason = models.TextField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["public_id"]),
        ]

    def __str__(self) -> str:
        return f"Payment #{self.id} for order {self.order_id}"


class PaymentEvent(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.payment_id}: {self.event_type}"


class PaymentAttempt(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="attempts")
    attempt_no = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=40, default="created")
    provider_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.payment_id}: attempt {self.attempt_no}"


class PaymentProviderCredentialRef(models.Model):
    provider = models.CharField(max_length=40, default="alfa")
    mode = models.CharField(max_length=20, default="test")
    credential_ref = models.CharField(max_length=240)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["provider", "mode"]

    def __str__(self) -> str:
        return f"{self.provider}:{self.mode}"
