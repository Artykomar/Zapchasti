from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.payments.models import Payment

from .models import FiscalReceipt, FiscalReceiptEvent, FiscalReceiptItem


@transaction.atomic
def create_test_sale_receipt_for_payment(payment: Payment) -> FiscalReceipt:
    payment = Payment.objects.select_for_update().select_related("order").get(pk=payment.pk)
    if payment.status != Payment.Status.SUCCEEDED:
        raise ValidationError("Fiscal receipt can be created only for succeeded payment.")

    existing_receipt = payment.fiscal_receipts.filter(receipt_type=FiscalReceipt.ReceiptType.SALE).first()
    if existing_receipt:
        return existing_receipt

    order = payment.order
    if order.total_amount_rub != payment.amount_rub:
        raise ValidationError("Payment amount does not match order amount.")

    receipt = FiscalReceipt.objects.create(
        payment=payment,
        order=order,
        receipt_type=FiscalReceipt.ReceiptType.SALE,
        status=FiscalReceipt.Status.VALIDATED,
        provider="mock",
        amount_rub=payment.amount_rub,
        currency=payment.currency,
        fiscal_number=f"mock-fn-{uuid.uuid4()}",
        fiscal_document=f"mock-fd-{uuid.uuid4()}",
        fiscal_sign=f"mock-fpd-{uuid.uuid4()}",
    )

    for order_item in order.items.all():
        FiscalReceiptItem.objects.create(
            receipt=receipt,
            name=(order_item.fiscal_name or order_item.part_name)[:128],
            article=order_item.article,
            quantity=order_item.quantity,
            unit_price_rub=order_item.unit_price_rub,
            line_total_rub=order_item.line_total_rub,
            vat_label=order_item.vat_label,
            payment_subject=order_item.payment_subject,
            payment_method=order_item.payment_method,
            unit=order_item.unit,
        )

    FiscalReceiptEvent.objects.create(
        receipt=receipt,
        event_type="mock_receipt_validated",
        payload={"payment_id": payment.id, "order_id": order.id},
    )
    return receipt
