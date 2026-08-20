from django.db import models


class FiscalReceipt(models.Model):
    class ReceiptType(models.TextChoices):
        SALE = "sale", "sale"
        REFUND = "refund", "refund"

    class Status(models.TextChoices):
        DRAFT = "draft", "draft"
        VALIDATED = "validated", "validated"
        SENT = "sent", "sent"
        FAILED = "failed", "failed"

    payment = models.ForeignKey("payments.Payment", on_delete=models.PROTECT, related_name="fiscal_receipts")
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="fiscal_receipts")
    refund = models.ForeignKey(
        "refunds.Refund",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="fiscal_receipts",
    )
    receipt_type = models.CharField(max_length=20, choices=ReceiptType.choices, default=ReceiptType.SALE)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.DRAFT)
    provider = models.CharField(max_length=40, default="mock")
    amount_rub = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="RUB")
    fiscal_number = models.CharField(max_length=120, blank=True)
    fiscal_document = models.CharField(max_length=120, blank=True)
    fiscal_sign = models.CharField(max_length=120, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment", "receipt_type"]),
            models.Index(fields=["status", "created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "receipt_type"],
                condition=models.Q(receipt_type="sale"),
                name="unique_sale_receipt_per_payment",
            ),
            models.UniqueConstraint(
                fields=["refund", "receipt_type"],
                condition=models.Q(receipt_type="refund"),
                name="unique_refund_receipt_per_refund",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.receipt_type} receipt for payment {self.payment_id}"


class FiscalReceiptItem(models.Model):
    receipt = models.ForeignKey(FiscalReceipt, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=128)
    article = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_rub = models.PositiveIntegerField(default=0)
    line_total_rub = models.PositiveIntegerField(default=0)
    vat_label = models.CharField(max_length=80, default="НДС не задан")
    payment_subject = models.CharField(max_length=80, default="commodity")
    payment_method = models.CharField(max_length=80, default="full_payment")
    unit = models.CharField(max_length=40, default="шт.")

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.name} x {self.quantity}"


class FiscalReceiptEvent(models.Model):
    receipt = models.ForeignKey(FiscalReceipt, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.receipt_id}: {self.event_type}"
