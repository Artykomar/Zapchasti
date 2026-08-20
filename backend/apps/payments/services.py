from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatusHistory

from .models import Payment, PaymentAttempt, PaymentEvent
from .providers import AlfaBankClient, PaymentProviderError


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


def _mark_order_paid(payment: Payment, note: str) -> None:
    if payment.status == Payment.Status.SUCCEEDED and payment.order.status == Order.Status.PAID:
        return
    payment.status = Payment.Status.SUCCEEDED
    payment.paid_at = payment.paid_at or timezone.now()
    payment.failure_reason = ""
    payment.save(update_fields=["status", "paid_at", "failure_reason", "updated_at"])
    payment.order.status = Order.Status.PAID
    payment.order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(order=payment.order, status=payment.order.status, note=note)
    if getattr(settings, "FISCALIZATION_ENABLED", False):
        from apps.fiscal.services import create_sale_receipt_for_payment

        create_sale_receipt_for_payment(payment)


def _mark_order_refunded(payment: Payment, *, full: bool, note: str) -> None:
    payment_status = Payment.Status.REFUNDED if full else Payment.Status.PARTIALLY_REFUNDED
    order_status = Order.Status.REFUNDED if full else Order.Status.PARTIALLY_REFUNDED
    if payment.status == payment_status and payment.order.status == order_status:
        return
    payment.status = payment_status
    payment.save(update_fields=["status", "updated_at"])
    payment.order.status = order_status
    payment.order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(order=payment.order, status=order_status, note=note)


def _mark_payment_failed(payment: Payment, reason: str, note: str) -> None:
    if payment.status == Payment.Status.SUCCEEDED:
        return
    payment.status = Payment.Status.FAILED
    payment.failure_reason = reason[:1000]
    payment.save(update_fields=["status", "failure_reason", "updated_at"])
    payment.order.status = Order.Status.FAILED
    payment.order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(order=payment.order, status=payment.order.status, note=note)


@transaction.atomic
def _create_payment_link_for_order(order: Order) -> tuple[Payment, str | None]:
    order = Order.objects.select_for_update().get(pk=order.pk)
    _ensure_payments_can_start(order)

    existing_payment = order.payments.filter(status=Payment.Status.PENDING).first()
    if existing_payment:
        return existing_payment, None

    attempt_number = order.payments.count() + 1
    mode = getattr(settings, "PAYMENTS_MODE", "test")
    provider = getattr(settings, "PAYMENTS_PROVIDER", "alfa")
    payment = Payment.objects.create(
        order=order,
        provider=provider,
        mode=mode,
        status=Payment.Status.DRAFT,
        amount_rub=order.total_amount_rub,
        currency=order.currency,
        provider_order_number=f"ZEMAZAP-{order.pk}-{attempt_number}",
        idempotency_key=f"order:{order.id}:amount:{order.total_amount_rub}:attempt:{attempt_number}",
    )

    if mode == "test" or provider == "mock":
        payment.bank_order_id = f"mock-{uuid.uuid4()}"
        payment.form_url = _mock_form_url(payment)
        provider_response = {"form_url": payment.form_url, "mode": payment.mode}
        attempt_status = "mock_link_created"
    elif provider == "alfa":
        try:
            registered = AlfaBankClient().register(payment)
        except PaymentProviderError as exc:
            payment.status = Payment.Status.FAILED
            payment.failure_reason = str(exc)[:1000]
            payment.save(update_fields=["status", "failure_reason", "updated_at"])
            PaymentEvent.objects.create(
                payment=payment,
                event_type="payment_registration_failed",
                payload={"error": str(exc)[:300]},
            )
            return payment, str(exc)
        payment.bank_order_id = registered.bank_order_id
        payment.form_url = registered.form_url
        provider_response = registered.raw
        attempt_status = "alfa_link_created"
    else:
        error_message = f"Unsupported payment provider: {provider}."
        payment.status = Payment.Status.FAILED
        payment.failure_reason = error_message
        payment.save(update_fields=["status", "failure_reason", "updated_at"])
        PaymentEvent.objects.create(payment=payment, event_type="payment_registration_failed")
        return payment, error_message

    payment.status = Payment.Status.PENDING
    payment.save(update_fields=["bank_order_id", "form_url", "status", "updated_at"])
    PaymentAttempt.objects.create(
        payment=payment,
        attempt_no=1,
        status=attempt_status,
        provider_response=provider_response,
    )
    PaymentEvent.objects.create(payment=payment, event_type="payment_link_created")

    order.status = Order.Status.PAYMENT_PENDING
    order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(order=order, status=order.status, note="Payment link created.")
    return payment, None


def create_payment_link_for_order(order: Order) -> Payment:
    payment, error_message = _create_payment_link_for_order(order)
    if error_message:
        raise PaymentConfigurationError(error_message)
    return payment


@transaction.atomic
def _synchronize_payment_status(payment: Payment) -> tuple[Payment, str | None]:
    payment = Payment.objects.select_for_update().select_related("order").get(pk=payment.pk)
    if payment.mode == "test" or payment.provider == "mock":
        raise PaymentConfigurationError("Server-to-server synchronization is only available for a real provider payment.")
    if payment.provider != "alfa" or not payment.bank_order_id:
        raise PaymentConfigurationError("Payment has no supported provider order identifier.")

    try:
        provider_status = AlfaBankClient().get_status(payment.bank_order_id)
    except PaymentProviderError as exc:
        PaymentEvent.objects.create(payment=payment, event_type="status_check_failed", payload={"error": str(exc)[:300]})
        return payment, str(exc)

    expected_minor = payment.amount_rub * 100
    if provider_status.order_number and provider_status.order_number != payment.provider_order_number:
        raise PaymentStateError("Alfa-Bank orderNumber does not match the internal payment.")
    if provider_status.amount_minor is not None and provider_status.amount_minor != expected_minor:
        raise PaymentStateError("Alfa-Bank payment amount does not match the internal payment.")
    if provider_status.deposited_amount_minor is not None and provider_status.order_status == 2:
        if provider_status.deposited_amount_minor != expected_minor:
            raise PaymentStateError("Alfa-Bank deposited amount does not match the internal payment.")
    if provider_status.currency and provider_status.currency not in {"643", "RUB"}:
        raise PaymentStateError("Alfa-Bank payment currency does not match RUB.")

    PaymentEvent.objects.create(payment=payment, event_type="status_checked", payload=provider_status.raw)
    refunded_minor = provider_status.refunded_amount_minor or 0
    if provider_status.order_status == 4 or refunded_minor >= expected_minor:
        _mark_order_refunded(payment, full=True, note="Alfa-Bank confirmed a full refund.")
    elif refunded_minor > 0:
        _mark_order_refunded(payment, full=False, note="Alfa-Bank confirmed a partial refund.")
    elif provider_status.order_status == 2:
        _mark_order_paid(payment, "Alfa-Bank server-to-server status confirmed payment.")
    elif provider_status.order_status in {3, 6}:
        _mark_payment_failed(payment, "Alfa-Bank reported a failed or cancelled payment.", "Alfa-Bank status failed.")
    return payment, None


def synchronize_payment_status(payment: Payment) -> Payment:
    synchronized_payment, error_message = _synchronize_payment_status(payment)
    if error_message:
        raise PaymentConfigurationError(error_message)
    return synchronized_payment


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
        _mark_order_paid(payment, "Mock payment paid.")
        PaymentEvent.objects.create(payment=payment, event_type="mock_callback_paid", payload={"status": status})
        return payment

    if normalized_status in {"failed", "fail", "declined", "cancelled"}:
        if payment.status == Payment.Status.SUCCEEDED:
            PaymentEvent.objects.create(payment=payment, event_type="mock_callback_ignored", payload={"status": status})
            return payment
        _mark_payment_failed(payment, "Mock payment failed.", "Mock payment failed.")
        PaymentEvent.objects.create(payment=payment, event_type="mock_callback_failed", payload={"status": status})
        return payment

    raise PaymentStateError("Unknown mock payment status.")
