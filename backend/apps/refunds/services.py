from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatusHistory
from apps.payments.models import Payment, PaymentEvent
from apps.payments.providers import AlfaBankClient, PaymentProviderError

from .models import Refund, RefundEvent


def refunded_amount(payment: Payment, *, exclude_refund_id: int | None = None) -> int:
    queryset = payment.refunds.filter(status=Refund.Status.SUCCEEDED)
    if exclude_refund_id:
        queryset = queryset.exclude(pk=exclude_refund_id)
    return sum(queryset.values_list("amount_rub", flat=True))


def validate_refund_amount(payment: Payment, amount_rub: int, *, exclude_refund_id: int | None = None) -> None:
    if payment.status not in {Payment.Status.SUCCEEDED, Payment.Status.PARTIALLY_REFUNDED}:
        raise ValidationError("Refund is available only for a succeeded payment.")
    if amount_rub <= 0:
        raise ValidationError("Refund amount must be positive.")
    remaining = payment.amount_rub - refunded_amount(payment, exclude_refund_id=exclude_refund_id)
    if amount_rub > remaining:
        raise ValidationError("Refund amount exceeds the remaining paid amount.")


def validate_refund_items(refund: Refund) -> None:
    items = list(refund.items.select_related("order_item"))
    if not items:
        return
    if sum(item.amount_rub for item in items) != refund.amount_rub:
        raise ValidationError("Refund item amounts must equal the refund amount.")
    for item in items:
        if item.order_item.order_id != refund.order_id:
            raise ValidationError("Refund item belongs to a different order.")
        if item.quantity <= 0 or item.quantity > item.order_item.quantity:
            raise ValidationError("Refund item quantity exceeds the purchased quantity.")
        if item.amount_rub <= 0:
            raise ValidationError("Refund item amount must be positive.")


@transaction.atomic
def create_refund(payment: Payment, amount_rub: int, reason: str, *, requested_by: str = "") -> Refund:
    payment = Payment.objects.select_for_update().select_related("order").get(pk=payment.pk)
    validate_refund_amount(payment, amount_rub)
    sequence = payment.refunds.count() + 1
    refund = Refund.objects.create(
        payment=payment,
        order=payment.order,
        amount_rub=amount_rub,
        reason=reason[:240],
        requested_by=requested_by[:160],
        idempotency_key=f"payment:{payment.pk}:refund:{sequence}:amount:{amount_rub}",
    )
    RefundEvent.objects.create(refund=refund, event_type="refund_requested")
    return refund


def process_refund(refund: Refund) -> Refund:
    with transaction.atomic():
        refund = Refund.objects.select_for_update().select_related("payment", "order").get(pk=refund.pk)
        if refund.status == Refund.Status.SUCCEEDED:
            return refund
        if refund.status not in {Refund.Status.REQUESTED, Refund.Status.APPROVED, Refund.Status.FAILED}:
            raise ValidationError("Refund is not in a processable status.")
        if refund.payment.order_id != refund.order_id:
            raise ValidationError("Refund payment belongs to a different order.")

        payment = Payment.objects.select_for_update().get(pk=refund.payment_id)
        validate_refund_amount(payment, refund.amount_rub, exclude_refund_id=refund.pk)
        validate_refund_items(refund)
        refund.status = Refund.Status.PROCESSING
        refund.save(update_fields=["status", "updated_at"])
        RefundEvent.objects.create(refund=refund, event_type="refund_processing")

    provider_payload = {}
    provider_reference = ""
    try:
        if payment.mode == "test" or payment.provider == "mock":
            provider_reference = f"mock-refund-{refund.public_id}"
        elif payment.provider == "alfa":
            provider_payload = AlfaBankClient().refund(payment.bank_order_id, refund.amount_rub)
            provider_reference = payment.bank_order_id
        else:
            raise PaymentProviderError(f"Unsupported refund provider: {payment.provider}.")
    except PaymentProviderError as exc:
        with transaction.atomic():
            refund = Refund.objects.select_for_update().get(pk=refund.pk)
            refund.status = Refund.Status.FAILED
            refund.manager_comment = str(exc)[:1000]
            refund.save(update_fields=["status", "manager_comment", "updated_at"])
            RefundEvent.objects.create(refund=refund, event_type="refund_failed", note=str(exc)[:500])
        raise ValidationError(str(exc)) from exc

    with transaction.atomic():
        refund = Refund.objects.select_for_update().select_related("order").get(pk=refund.pk)
        payment = Payment.objects.select_for_update().select_related("order").get(pk=refund.payment_id)
        if refund.status != Refund.Status.PROCESSING:
            raise ValidationError("Refund state changed while the provider request was running.")
        validate_refund_amount(payment, refund.amount_rub, exclude_refund_id=refund.pk)
        refund.status = Refund.Status.SUCCEEDED
        refund.provider_reference = provider_reference
        refund.processed_at = timezone.now()
        refund.save(update_fields=["status", "provider_reference", "processed_at", "updated_at"])
        RefundEvent.objects.create(refund=refund, event_type="refund_succeeded", payload=provider_payload)

        total_refunded = refunded_amount(payment)
        is_full = total_refunded >= payment.amount_rub
        payment.status = Payment.Status.REFUNDED if is_full else Payment.Status.PARTIALLY_REFUNDED
        payment.save(update_fields=["status", "updated_at"])
        payment.order.status = Order.Status.REFUNDED if is_full else Order.Status.PARTIALLY_REFUNDED
        payment.order.save(update_fields=["status", "updated_at"])
        OrderStatusHistory.objects.create(
            order=payment.order,
            status=payment.order.status,
            note=f"Refund #{refund.pk} completed for {refund.amount_rub} RUB.",
        )
        PaymentEvent.objects.create(
            payment=payment,
            event_type="refund_succeeded",
            payload={"refund_id": refund.pk, "amount_rub": refund.amount_rub},
        )
    if getattr(settings, "FISCALIZATION_ENABLED", False):
        from apps.fiscal.services import create_refund_receipt_for_refund

        create_refund_receipt_for_refund(refund)
    return refund
