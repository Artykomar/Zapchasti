from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "draft"
        CONFIRMED_BY_MANAGER = "confirmed_by_manager", "confirmed by manager"
        PAYMENT_PENDING = "payment_pending", "payment pending"
        PAID = "paid", "paid"
        FAILED = "failed", "failed"
        CANCELLED = "cancelled", "cancelled"
        FULFILLED = "fulfilled", "fulfilled"
        REFUNDED = "refunded", "refunded"
        PARTIALLY_REFUNDED = "partially_refunded", "partially refunded"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    request = models.OneToOneField(
        "leads.CustomerRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
    )
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.DRAFT)
    customer_name = models.CharField(max_length=160)
    contact = models.CharField(max_length=160)
    vehicle = models.CharField(max_length=240, blank=True)
    manager_note = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default="RUB")
    total_amount_rub = models.PositiveIntegerField(default=0)
    delivery_terms = models.CharField(max_length=240, blank=True)
    warranty_terms = models.CharField(max_length=240, blank=True)
    vat_label = models.CharField(max_length=80, default="НДС не задан")
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.status}"

    @property
    def can_create_payment(self) -> bool:
        return self.status in {self.Status.CONFIRMED_BY_MANAGER, self.Status.PAYMENT_PENDING}

    def recalculate_total(self, save: bool = True) -> int:
        total = sum(item.line_total_rub for item in self.items.all())
        self.total_amount_rub = total
        if save:
            self.save(update_fields=["total_amount_rub", "updated_at"])
        return total

    def mark_confirmed(self, note: str = "") -> None:
        self.status = self.Status.CONFIRMED_BY_MANAGER
        self.confirmed_at = timezone.now()
        self.save(update_fields=["status", "confirmed_at", "updated_at"])
        OrderStatusHistory.objects.create(order=self, status=self.status, note=note)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    part = models.ForeignKey(
        "catalog.Part",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    part_name = models.CharField(max_length=240)
    article = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_rub = models.PositiveIntegerField(default=0)
    line_total_rub = models.PositiveIntegerField(default=0)
    condition_snapshot = models.CharField(max_length=120, blank=True)
    delivery_snapshot = models.CharField(max_length=160, blank=True)
    warranty_snapshot = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.line_total_rub = self.unit_price_rub * self.quantity
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.part_name} x {self.quantity}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=40, choices=Order.Status.choices)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.order_id}: {self.status}"


class OrderComment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="comments")
    author = models.CharField(max_length=160, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Comment for order {self.order_id}"
