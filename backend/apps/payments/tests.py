from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from unittest.mock import patch

from apps.leads.serializers import CustomerRequestCreateSerializer
from apps.orders.models import Order
from apps.orders.services import create_order_from_request

from .models import Payment
from .providers import ProviderPaymentStatus, RegisteredPayment, build_alfa_order_bundle
from .providers import PaymentProviderError
from .services import apply_mock_payment_callback, create_payment_link_for_order, synchronize_payment_status


class PaymentWorkflowTests(TestCase):
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

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="test", PAYMENTS_PROVIDER="alfa")
    def test_create_payment_link_for_confirmed_order(self):
        order = self.create_confirmed_order()

        payment = create_payment_link_for_order(order)

        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.amount_rub, 34700)
        self.assertIn(str(order.token), payment.form_url)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAYMENT_PENDING)

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="test", PAYMENTS_PROVIDER="alfa")
    def test_mock_callback_marks_order_paid_idempotently(self):
        order = self.create_confirmed_order()
        payment = create_payment_link_for_order(order)

        paid_payment = apply_mock_payment_callback(str(payment.public_id), "paid")
        second_paid_payment = apply_mock_payment_callback(str(payment.public_id), "paid")

        self.assertEqual(paid_payment.status, Payment.Status.SUCCEEDED)
        self.assertEqual(second_paid_payment.status, Payment.Status.SUCCEEDED)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="prod", PAYMENTS_PROVIDER="alfa")
    @patch("apps.payments.services.AlfaBankClient")
    def test_real_provider_registration_saves_bank_identifiers(self, client_class):
        order = self.create_confirmed_order()
        client_class.return_value.register.return_value = RegisteredPayment(
            bank_order_id="alfa-order-id",
            form_url="https://pay.alfabank.ru/payment/merchants/example/payment_ru.html",
            raw={"errorCode": "0"},
        )

        payment = create_payment_link_for_order(order)

        self.assertEqual(payment.bank_order_id, "alfa-order-id")
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertTrue(payment.provider_order_number.startswith("ZEMAZAP-"))
        client_class.return_value.register.assert_called_once()

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="prod", PAYMENTS_PROVIDER="alfa")
    @patch("apps.payments.services.AlfaBankClient")
    def test_real_provider_registration_failure_is_journaled(self, client_class):
        order = self.create_confirmed_order()
        client_class.return_value.register.side_effect = PaymentProviderError("gateway unavailable")

        with self.assertRaisesMessage(Exception, "gateway unavailable"):
            create_payment_link_for_order(order)

        payment = order.payments.get()
        self.assertEqual(payment.status, Payment.Status.FAILED)
        self.assertTrue(payment.events.filter(event_type="payment_registration_failed").exists())

    def test_alfa_fiscal_order_bundle_uses_minor_units_and_item_snapshots(self):
        order = self.create_confirmed_order()

        bundle = build_alfa_order_bundle(order)
        item = bundle["cartItems"]["items"][0]

        self.assertEqual(item["itemAmount"], 3_470_000)
        self.assertEqual(item["itemPrice"], 3_470_000)
        self.assertEqual(item["quantity"]["value"], 1)
        self.assertNotIn("contact", str(bundle).lower())

    @override_settings(PAYMENTS_ENABLED=False)
    def test_payment_link_requires_feature_flag(self):
        order = self.create_confirmed_order()

        with self.assertRaisesMessage(Exception, "PAYMENTS_ENABLED=false"):
            create_payment_link_for_order(order)

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="test", PAYMENTS_PROVIDER="alfa")
    def test_staff_api_creates_payment_link(self):
        order = self.create_confirmed_order()
        user = get_user_model().objects.create_superuser("admin", "admin@example.ru", "pass")
        self.client.force_login(user)

        response = self.client.post("/api/payments/create-link/", data={"orderToken": str(order.token)})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], Payment.Status.PENDING)

    @override_settings(PAYMENTS_ENABLED=True, PAYMENTS_MODE="test", PAYMENTS_PROVIDER="alfa")
    def test_mock_decline_marks_payment_and_order_failed(self):
        order = self.create_confirmed_order()
        payment = create_payment_link_for_order(order)

        apply_mock_payment_callback(str(payment.public_id), "declined")

        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.FAILED)
        self.assertEqual(order.status, Order.Status.FAILED)

    @override_settings(PAYMENTS_MODE="prod", PAYMENTS_PROVIDER="alfa")
    @patch("apps.payments.services.AlfaBankClient")
    def test_server_to_server_status_marks_verified_payment_paid(self, client_class):
        order = self.create_confirmed_order()
        order.status = Order.Status.PAYMENT_PENDING
        order.save(update_fields=["status"])
        payment = Payment.objects.create(
            order=order,
            provider="alfa",
            mode="prod",
            status=Payment.Status.PENDING,
            amount_rub=order.total_amount_rub,
            currency="RUB",
            bank_order_id="bank-1",
            provider_order_number="ZEMAZAP-1-1",
            idempotency_key="s2s-paid",
        )
        client_class.return_value.get_status.return_value = ProviderPaymentStatus(
            order_status=2,
            order_number="ZEMAZAP-1-1",
            amount_minor=3_470_000,
            deposited_amount_minor=3_470_000,
            refunded_amount_minor=0,
            currency="643",
            raw={"orderStatus": 2, "orderNumber": "ZEMAZAP-1-1", "amount": 3_470_000},
        )

        synchronize_payment_status(payment)
        history_count = order.status_history.count()
        synchronize_payment_status(payment)

        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.SUCCEEDED)
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.status_history.count(), history_count)

    @override_settings(PAYMENTS_MODE="prod", PAYMENTS_PROVIDER="alfa")
    @patch("apps.payments.services.AlfaBankClient")
    def test_server_to_server_status_preserves_partial_refund(self, client_class):
        order = self.create_confirmed_order()
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
        payment = Payment.objects.create(
            order=order,
            provider="alfa",
            mode="prod",
            status=Payment.Status.SUCCEEDED,
            amount_rub=order.total_amount_rub,
            currency="RUB",
            bank_order_id="bank-partial-refund",
            provider_order_number="ZEMAZAP-PARTIAL",
            idempotency_key="s2s-partial-refund",
        )
        client_class.return_value.get_status.return_value = ProviderPaymentStatus(
            order_status=2,
            order_number="ZEMAZAP-PARTIAL",
            amount_minor=3_470_000,
            deposited_amount_minor=3_470_000,
            refunded_amount_minor=1_000_000,
            currency="643",
            raw={"orderStatus": 2, "orderNumber": "ZEMAZAP-PARTIAL"},
        )

        synchronize_payment_status(payment)

        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PARTIALLY_REFUNDED)
        self.assertEqual(order.status, Order.Status.PARTIALLY_REFUNDED)

    @override_settings(PAYMENTS_MODE="prod", PAYMENTS_PROVIDER="alfa")
    @patch("apps.payments.services.AlfaBankClient")
    def test_server_to_server_status_rejects_wrong_amount(self, client_class):
        order = self.create_confirmed_order()
        order.status = Order.Status.PAYMENT_PENDING
        order.save(update_fields=["status"])
        payment = Payment.objects.create(
            order=order,
            provider="alfa",
            mode="prod",
            status=Payment.Status.PENDING,
            amount_rub=order.total_amount_rub,
            currency="RUB",
            bank_order_id="bank-2",
            provider_order_number="ZEMAZAP-2-1",
            idempotency_key="s2s-wrong-amount",
        )
        client_class.return_value.get_status.return_value = ProviderPaymentStatus(
            order_status=2,
            order_number="ZEMAZAP-2-1",
            amount_minor=1,
            deposited_amount_minor=1,
            refunded_amount_minor=0,
            currency="643",
            raw={"orderStatus": 2},
        )

        with self.assertRaisesMessage(Exception, "amount does not match"):
            synchronize_payment_status(payment)

    @override_settings(PAYMENTS_MODE="prod", PAYMENTS_PROVIDER="alfa")
    @patch("apps.payments.services.AlfaBankClient")
    def test_server_to_server_gateway_failure_is_journaled(self, client_class):
        order = self.create_confirmed_order()
        payment = Payment.objects.create(
            order=order,
            provider="alfa",
            mode="prod",
            status=Payment.Status.PENDING,
            amount_rub=order.total_amount_rub,
            currency="RUB",
            bank_order_id="bank-status-failure",
            provider_order_number="ZEMAZAP-STATUS-FAILURE",
            idempotency_key="s2s-status-failure",
        )
        client_class.return_value.get_status.side_effect = PaymentProviderError("gateway unavailable")

        with self.assertRaisesMessage(Exception, "gateway unavailable"):
            synchronize_payment_status(payment)

        self.assertTrue(payment.events.filter(event_type="status_check_failed").exists())

    @override_settings(
        PAYMENTS_MODE="prod",
        PAYMENTS_PROVIDER="alfa",
        ALFA_BANK_CALLBACK_TOKEN="callback-secret",
    )
    @patch("apps.payments.views.synchronize_payment_status")
    def test_alfa_callback_requires_secret_token_and_uses_server_check(self, synchronize):
        order = self.create_confirmed_order()
        payment = Payment.objects.create(
            order=order,
            provider="alfa",
            mode="prod",
            status=Payment.Status.PENDING,
            amount_rub=order.total_amount_rub,
            currency="RUB",
            bank_order_id="callback-bank-order",
            provider_order_number="ZEMAZAP-CALLBACK",
            idempotency_key="callback-test",
        )
        synchronize.return_value = payment

        forbidden = self.client.post(
            "/api/payments/alfa/callback/",
            data={"orderId": payment.bank_order_id},
        )
        accepted = self.client.post(
            "/api/payments/alfa/callback/?token=callback-secret",
            data={"orderId": payment.bank_order_id, "status": "paid"},
        )

        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(accepted.status_code, 200)
        synchronize.assert_called_once()
