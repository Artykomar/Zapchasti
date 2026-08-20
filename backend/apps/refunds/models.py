from __future__ import annotations

import uuid

from django.db import models


class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "requested"
        APPROVED = "approved", "approved"
        PROCESSING = "processing", "processing"
        SUCCEEDED = "succeeded", "succeeded"
        FAILED = "failed", "failed"
        CANCELLED = "cancelled", "cancelled"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    payment = models.ForeignKey("payments.Payment", on_delete=models.PROTECT, related_name="refunds")
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="refunds")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.REQUESTED)
    amount_rub = models.PositiveIntegerField()
    reason = models.CharField(max_length=240)
    manager_comment = models.TextField(blank=True)
    provider_reference = models.CharField(max_length=160, blank=True)
    idempotency_key = models.CharField(max_length=180, unique=True)
    requested_by = models.CharField(max_length=160, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["payment", "status"]), models.Index(fields=["order", "status"])]
        permissions = [("process_refund", "Can process payment refunds")]

    def __str__(self) -> str:
        return f"Refund #{self.pk} for order {self.order_id}"


class RefundItem(models.Model):
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.PROTECT, related_name="refund_items")
    quantity = models.PositiveIntegerField(default=1)
    amount_rub = models.PositiveIntegerField(default=0)
    condition_note = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.order_item} — {self.amount_rub} RUB"


class RefundEvent(models.Model):
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=80)
    note = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.refund_id}: {self.event_type}"


class Claim(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "new"
        IN_REVIEW = "in_review", "in review"
        WAITING_CUSTOMER = "waiting_customer", "waiting customer"
        APPROVED = "approved", "approved"
        REJECTED = "rejected", "rejected"
        RESOLVED = "resolved", "resolved"

    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="claims")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    claim_type = models.CharField(max_length=80, default="quality")
    customer_name = models.CharField(max_length=160)
    contact = models.CharField(max_length=160)
    description = models.TextField()
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [("view_claim_pii", "Can view personal data in claims")]

    def __str__(self) -> str:
        return f"Claim #{self.pk} — {self.status}"
