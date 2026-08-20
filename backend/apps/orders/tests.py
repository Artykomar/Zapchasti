from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import RequestFactory
from django.test import TestCase

from apps.leads.models import CustomerRequest
from apps.leads.serializers import CustomerRequestCreateSerializer

from .models import Order
from .admin import OrderAdmin
from .services import create_order_from_request


class OrderWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def test_create_order_from_request_copies_snapshot_items(self):
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
                        "quantity": 2,
                        "price": 34700,
                    }
                ],
            }
        )
        serializer.is_valid(raise_exception=True)
        customer_request = serializer.save()

        order, created = create_order_from_request(customer_request)

        self.assertTrue(created)
        self.assertEqual(order.status, Order.Status.DRAFT)
        self.assertEqual(order.total_amount_rub, 69400)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.status_history.count(), 1)

    def test_create_order_from_request_is_idempotent(self):
        customer_request = CustomerRequest.objects.create(
            customer_name="Артём",
            contact="+7 999 111-22-33",
            request_text="Нужна фара",
            source=CustomerRequest.Source.REQUEST_FORM,
            privacy_accepted=True,
        )

        first_order, first_created = create_order_from_request(customer_request)
        second_order, second_created = create_order_from_request(customer_request)

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first_order, second_order)

    def test_accountant_cannot_view_order_pii_but_manager_can(self):
        call_command("bootstrap_roles", verbosity=0)
        accountant = get_user_model().objects.create_user("accountant")
        accountant.groups.add(Group.objects.get(name="accountant"))
        manager = get_user_model().objects.create_user("manager")
        manager.groups.add(Group.objects.get(name="manager"))
        model_admin = OrderAdmin(Order, admin.site)
        request = RequestFactory().get("/admin/orders/order/")

        request.user = accountant
        self.assertIn("contact", model_admin.get_exclude(request))
        self.assertIn("masked_customer", model_admin.get_list_display(request))

        request.user = manager
        self.assertNotIn("contact", model_admin.get_exclude(request))
        self.assertIn("customer_name", model_admin.get_list_display(request))
