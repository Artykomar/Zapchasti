from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.payments.models import Payment

from .models import FiscalReceipt, FiscalReceiptEvent, FiscalReceiptItem


def _provider_status() -> tuple[str, str]:
    provider = str(getattr(settings, "FISCAL_PROVIDER", "mock"))
    return provider, FiscalReceipt.Status.SENT if provider == "alfa" else FiscalReceipt.Status.VALIDATED


def _copy_order_items(receipt: FiscalReceipt) -> None:
    for order_item in receipt.order.items.all():
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


@transaction.atomic
def create_sale_receipt_for_payment(payment: Payment) -> FiscalReceipt:
    payment = Payment.objects.select_for_update().select_related("order").get(pk=payment.pk)
    if payment.status != Payment.Status.SUCCEEDED:
        raise ValidationError("Fiscal receipt can be created only for succeeded payment.")

    existing_receipt = payment.fiscal_receipts.filter(receipt_type=FiscalReceipt.ReceiptType.SALE).first()
    if existing_receipt:
        return existing_receipt

    order = payment.order
    if order.total_amount_rub != payment.amount_rub:
        raise ValidationError("Payment amount does not match order amount.")

    provider, receipt_status = _provider_status()
    receipt = FiscalReceipt.objects.create(
        payment=payment,
        order=order,
        receipt_type=FiscalReceipt.ReceiptType.SALE,
        status=receipt_status,
        provider=provider,
        amount_rub=payment.amount_rub,
        currency=payment.currency,
        fiscal_number=f"mock-fn-{uuid.uuid4()}" if provider == "mock" else "",
        fiscal_document=f"mock-fd-{uuid.uuid4()}" if provider == "mock" else "",
        fiscal_sign=f"mock-fpd-{uuid.uuid4()}" if provider == "mock" else "",
    )
    _copy_order_items(receipt)
    FiscalReceiptEvent.objects.create(
        receipt=receipt,
        event_type="mock_receipt_validated" if provider == "mock" else "alfa_order_bundle_submitted",
        payload={"payment_id": payment.id, "order_id": order.id},
    )
    return receipt


def create_test_sale_receipt_for_payment(payment: Payment) -> FiscalReceipt:
    return create_sale_receipt_for_payment(payment)


@transaction.atomic
def create_refund_receipt_for_refund(refund) -> FiscalReceipt:
    from apps.refunds.models import Refund

    refund = Refund.objects.select_for_update().select_related("payment", "order").get(pk=refund.pk)
    if refund.status != Refund.Status.SUCCEEDED:
        raise ValidationError("Refund receipt can be created only for a succeeded refund.")
    existing = refund.fiscal_receipts.filter(receipt_type=FiscalReceipt.ReceiptType.REFUND).first()
    if existing:
        return existing

    provider, receipt_status = _provider_status()
    receipt = FiscalReceipt.objects.create(
        payment=refund.payment,
        order=refund.order,
        refund=refund,
        receipt_type=FiscalReceipt.ReceiptType.REFUND,
        status=receipt_status,
        provider=provider,
        amount_rub=refund.amount_rub,
        currency=refund.payment.currency,
        fiscal_number=f"mock-refund-fn-{uuid.uuid4()}" if provider == "mock" else "",
        fiscal_document=f"mock-refund-fd-{uuid.uuid4()}" if provider == "mock" else "",
        fiscal_sign=f"mock-refund-fpd-{uuid.uuid4()}" if provider == "mock" else "",
    )
    refund_items = list(refund.items.select_related("order_item"))
    if refund_items:
        for refund_item in refund_items:
            order_item = refund_item.order_item
            FiscalReceiptItem.objects.create(
                receipt=receipt,
                name=(order_item.fiscal_name or order_item.part_name)[:128],
                article=order_item.article,
                quantity=refund_item.quantity,
                unit_price_rub=refund_item.amount_rub // max(1, refund_item.quantity),
                line_total_rub=refund_item.amount_rub,
                vat_label=order_item.vat_label,
                payment_subject=order_item.payment_subject,
                payment_method="full_payment",
                unit=order_item.unit,
            )
    else:
        FiscalReceiptItem.objects.create(
            receipt=receipt,
            name=f"Возврат по заказу #{refund.order_id}",
            quantity=1,
            unit_price_rub=refund.amount_rub,
            line_total_rub=refund.amount_rub,
            vat_label=refund.order.vat_label,
        )
    FiscalReceiptEvent.objects.create(
        receipt=receipt,
        event_type="mock_refund_receipt_validated" if provider == "mock" else "alfa_refund_submitted",
        payload={"refund_id": refund.pk, "payment_id": refund.payment_id},
    )
    return receipt


@transaction.atomic
def retry_failed_receipt(receipt: FiscalReceipt) -> FiscalReceipt:
    receipt = FiscalReceipt.objects.select_for_update().get(pk=receipt.pk)
    if receipt.status != FiscalReceipt.Status.FAILED:
        return receipt
    provider, receipt_status = _provider_status()
    receipt.provider = provider
    receipt.status = receipt_status
    receipt.error_message = ""
    receipt.save(update_fields=["provider", "status", "error_message", "updated_at"])
    FiscalReceiptEvent.objects.create(receipt=receipt, event_type="receipt_retry_scheduled")
    return receipt
