from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from unittest.mock import patch

from apps.leads.serializers import CustomerRequestCreateSerializer
from apps.orders.services import create_order_from_request
from apps.payments.models import Payment

from apps.payments.providers import PaymentProviderError

from .models import Refund, RefundItem
from .services import create_refund, process_refund


class RefundWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def create_paid_payment(self) -> Payment:
        serializer = CustomerRequestCreateSerializer(
            data={
                "customerName": "Тестовый клиент",
                "contact": "+7 999 000-00-00",
                "requestText": "Корзина",
                "source": "cart",
                "privacyAccepted": True,
                "items": [
                    {
                        "id": "octavia-led-headlamp-left",
                        "name": "Фара светодиодная левая",
                        "article": "ZP-LGT-5015L",
                        "quantity": 1,
                        "price": 34700,
                    }
                ],
            }
        )
        serializer.is_valid(raise_exception=True)
        order, _created = create_order_from_request(serializer.save())
        order.mark_confirmed("Test")
        return Payment.objects.create(
            order=order,
            provider="mock",
            mode="test",
            status=Payment.Status.SUCCEEDED,
            amount_rub=order.total_amount_rub,
            currency="RUB",
            bank_order_id="mock-paid",
            idempotency_key=f"refund-test-{order.pk}",
        )

    @override_settings(FISCALIZATION_ENABLED=False)
    def test_partial_and_full_refund_workflow(self):
        payment = self.create_paid_payment()
        first = process_refund(create_refund(payment, 10_000, "Частичный возврат"))
        payment.refresh_from_db()
        self.assertEqual(first.status, Refund.Status.SUCCEEDED)
        self.assertEqual(payment.status, Payment.Status.PARTIALLY_REFUNDED)

        second = process_refund(create_refund(payment, 24_700, "Остаток"))
        payment.refresh_from_db()
        payment.order.refresh_from_db()
        self.assertEqual(second.status, Refund.Status.SUCCEEDED)
        self.assertEqual(payment.status, Payment.Status.REFUNDED)
        self.assertEqual(payment.order.status, "refunded")

    def test_refund_cannot_exceed_paid_amount(self):
        payment = self.create_paid_payment()
        with self.assertRaisesMessage(Exception, "exceeds"):
            create_refund(payment, payment.amount_rub + 1, "Слишком много")

    def test_refund_item_amounts_must_match_refund(self):
        payment = self.create_paid_payment()
        refund = create_refund(payment, 10_000, "Возврат позиции")
        RefundItem.objects.create(
            refund=refund,
            order_item=payment.order.items.get(),
            quantity=1,
            amount_rub=9_999,
        )

        with self.assertRaisesMessage(ValidationError, "must equal"):
            process_refund(refund)

    @override_settings(FISCALIZATION_ENABLED=False)
    @patch("apps.refunds.services.AlfaBankClient")
    def test_provider_failure_is_persisted_for_safe_retry(self, client_class):
        payment = self.create_paid_payment()
        payment.provider = "alfa"
        payment.mode = "prod"
        payment.bank_order_id = "alfa-refund-failure"
        payment.save(update_fields=["provider", "mode", "bank_order_id"])
        refund = create_refund(payment, 10_000, "Сетевая ошибка")
        client_class.return_value.refund.side_effect = PaymentProviderError("gateway unavailable")

        with self.assertRaisesMessage(ValidationError, "gateway unavailable"):
            process_refund(refund)

        refund.refresh_from_db()
        self.assertEqual(refund.status, Refund.Status.FAILED)
        self.assertTrue(refund.events.filter(event_type="refund_failed").exists())
