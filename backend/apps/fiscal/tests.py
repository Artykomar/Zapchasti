from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.orders.models import Order
from apps.orders.services import create_order_from_request
from apps.payments.models import Payment
from apps.leads.serializers import CustomerRequestCreateSerializer

from .models import FiscalReceipt
from .services import create_test_sale_receipt_for_payment


class FiscalReceiptTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def create_confirmed_order(self) -> Order:
        serializer = CustomerRequestCreateSerializer(
            data={
                "customerName": "Артём",
                "contact": "+7 999 111-22-33",
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
        customer_request = serializer.save()
        order, _created = create_order_from_request(customer_request)
        order.mark_confirmed("Test confirmation.")
        return order

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="test", FISCALIZATION_ENABLED=True)
    def test_create_test_sale_receipt_for_paid_payment(self):
        order = self.create_confirmed_order()
        payment = Payment.objects.create(
            order=order,
            provider="alfa",
            mode="test",
            status=Payment.Status.SUCCEEDED,
            amount_rub=order.total_amount_rub,
            currency=order.currency,
            bank_order_id="mock-bank-order",
            idempotency_key="fiscal-test-payment",
        )

        receipt = create_test_sale_receipt_for_payment(payment)

        self.assertEqual(receipt.status, FiscalReceipt.Status.VALIDATED)
        self.assertEqual(receipt.amount_rub, order.total_amount_rub)
        self.assertEqual(receipt.items.count(), order.items.count())

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="test", FISCALIZATION_ENABLED=True)
    def test_paid_mock_callback_creates_receipt_when_enabled(self):
        order = self.create_confirmed_order()
        from apps.payments.services import apply_mock_payment_callback, create_payment_link_for_order

        payment = create_payment_link_for_order(order)
        apply_mock_payment_callback(str(payment.public_id), "paid")

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(FiscalReceipt.objects.filter(payment=payment).count(), 1)

    @override_settings(FISCALIZATION_ENABLED=True, FISCAL_PROVIDER="mock")
    def test_successful_refund_creates_refund_receipt(self):
        from apps.refunds.services import create_refund, process_refund

        order = self.create_confirmed_order()
        payment = Payment.objects.create(
            order=order,
            provider="mock",
            mode="test",
            status=Payment.Status.SUCCEEDED,
            amount_rub=order.total_amount_rub,
            currency=order.currency,
            bank_order_id="mock-refund-payment",
            idempotency_key="fiscal-refund-payment",
        )

        refund = process_refund(create_refund(payment, 10_000, "Частичный возврат"))

        receipt = FiscalReceipt.objects.get(refund=refund)
        self.assertEqual(receipt.receipt_type, FiscalReceipt.ReceiptType.REFUND)
        self.assertEqual(receipt.status, FiscalReceipt.Status.VALIDATED)
        self.assertEqual(receipt.amount_rub, 10_000)
