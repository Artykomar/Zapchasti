from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatusHistory

from .models import Payment, PaymentAttempt, PaymentEvent


class PaymentConfigurationError(ValidationError):
    pass


class PaymentStateError(ValidationError):
    pass


def _mock_form_url(payment: Payment) -> str:
    base_url = getattr(settings, "ZEMAZAP_SITE_URL", "http://127.0.0.1:3000").rstrip("/")
    return f"{base_url}/orders/{payment.order.token}?payment={payment.public_id}"


def _ensure_payments_can_start(order: Order) -> None:
    if not getattr(settings, "PAYMENTS_ENABLED", False):
        raise PaymentConfigurationError("Payments are disabled by PAYMENTS_ENABLED=false.")
    if not order.can_create_payment:
        raise PaymentStateError("Payment link can be created only for confirmed orders.")
    if order.total_amount_rub <= 0:
        raise PaymentStateError("Payment link cannot be created for zero amount order.")
    if order.payments.filter(status=Payment.Status.SUCCEEDED).exists():
        raise PaymentStateError("Order is already paid.")


@transaction.atomic
def create_payment_link_for_order(order: Order) -> Payment:
    order = Order.objects.select_for_update().get(pk=order.pk)
    _ensure_payments_can_start(order)

    existing_payment = order.payments.filter(status=Payment.Status.PENDING).first()
    if existing_payment:
        return existing_payment

    payment = Payment.objects.create(
        order=order,
        provider=getattr(settings, "PAYMENTS_PROVIDER", "alfa"),
        mode=getattr(settings, "PAYMENTS_MODE", "test"),
        status=Payment.Status.PENDING,
        amount_rub=order.total_amount_rub,
        currency=order.currency,
        bank_order_id=f"mock-{uuid.uuid4()}",
        idempotency_key=f"order:{order.id}:amount:{order.total_amount_rub}:attempt:{order.payments.count() + 1}",
    )
    payment.form_url = _mock_form_url(payment)
    payment.save(update_fields=["form_url", "updated_at"])
    PaymentAttempt.objects.create(
        payment=payment,
        attempt_no=1,
        status="mock_link_created",
        provider_response={"form_url": payment.form_url, "mode": payment.mode},
    )
    PaymentEvent.objects.create(payment=payment, event_type="payment_link_created")

    order.status = Order.Status.PAYMENT_PENDING
    order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(order=order, status=order.status, note="Mock payment link created.")
    return payment


@transaction.atomic
def apply_mock_payment_callback(public_id: str, status: str) -> Payment:
    if getattr(settings, "PAYMENTS_MODE", "test") != "test":
        raise PaymentConfigurationError("Mock callbacks are allowed only in PAYMENTS_MODE=test.")

    payment = Payment.objects.select_for_update().select_related("order").get(public_id=public_id)
    normalized_status = status.strip().lower()

    if normalized_status in {"paid", "succeeded", "success"}:
        if payment.status == Payment.Status.SUCCEEDED:
            PaymentEvent.objects.create(payment=payment, event_type="mock_callback_duplicate", payload={"status": status})
            return payment
        payment.status = Payment.Status.SUCCEEDED
        payment.paid_at = payment.paid_at or timezone.now()
        payment.failure_reason = ""
        payment.save(update_fields=["status", "paid_at", "failure_reason", "updated_at"])
        payment.order.status = Order.Status.PAID
        payment.order.save(update_fields=["status", "updated_at"])
        OrderStatusHistory.objects.create(order=payment.order, status=payment.order.status, note="Mock payment paid.")
        PaymentEvent.objects.create(payment=payment, event_type="mock_callback_paid", payload={"status": status})
        if getattr(settings, "FISCALIZATION_ENABLED", False):
            from apps.fiscal.services import create_test_sale_receipt_for_payment

            create_test_sale_receipt_for_payment(payment)
        return payment

    if normalized_status in {"failed", "fail", "declined"}:
        if payment.status == Payment.Status.SUCCEEDED:
            PaymentEvent.objects.create(payment=payment, event_type="mock_callback_ignored", payload={"status": status})
            return payment
        payment.status = Payment.Status.FAILED
        payment.failure_reason = "Mock payment failed."
        payment.save(update_fields=["status", "failure_reason", "updated_at"])
        payment.order.status = Order.Status.FAILED
        payment.order.save(update_fields=["status", "updated_at"])
        OrderStatusHistory.objects.create(order=payment.order, status=payment.order.status, note="Mock payment failed.")
        PaymentEvent.objects.create(payment=payment, event_type="mock_callback_failed", payload={"status": status})
        return payment

    raise PaymentStateError("Unknown mock payment status.")
