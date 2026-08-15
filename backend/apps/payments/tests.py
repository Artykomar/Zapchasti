from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.leads.serializers import CustomerRequestCreateSerializer
from apps.orders.models import Order
from apps.orders.services import create_order_from_request

from .models import Payment
from .services import apply_mock_payment_callback, create_payment_link_for_order


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
