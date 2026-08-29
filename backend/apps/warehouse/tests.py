import uuid
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.catalog.models import Brand, Category, Manufacturer, Part, PriceOffer, Supplier
from apps.orders.models import Order, OrderItem
from . import cdek
from .forms import ShipmentForm
from .models import Fulfillment, PurchaseLine, PurchaseOrder, Shipment, StockItem, StockMovement, WarehouseEvent
from .services import adjust_stock, process_order, receive_purchase, set_purchase_status


class WarehouseFixture(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("bootstrap_roles", verbosity=0)
        cls.user = get_user_model().objects.create_user("warehouse-test", is_staff=True)
        cls.user.groups.add(Group.objects.get(name="warehouse_manager"))
        brand = Brand.objects.create(name="Марка", slug="warehouse-brand")
        category = Category.objects.create(name="Фильтры", slug="warehouse-category")
        manufacturer = Manufacturer.objects.create(name="Производитель")
        cls.part = Part.objects.create(name="Фильтр масляный", slug="warehouse-filter", primary_article="FLT-100", brand=brand, category=category, manufacturer=manufacturer)
        cls.part2 = Part.objects.create(name="Фильтр воздушный", slug="warehouse-filter-2", primary_article="FLT-200", brand=brand, category=category, manufacturer=manufacturer)
        cls.supplier = Supplier.objects.create(name="Тестовый поставщик", kind="test")
        cls.offer = PriceOffer.objects.create(part=cls.part, supplier=cls.supplier, price_rub=500, stock="100 у поставщика")
        cls.order = Order.objects.create(customer_name="Тестовый получатель", contact="+79990000001", status=Order.Status.PAID, total_amount_rub=1000)
        OrderItem.objects.create(order=cls.order, part=cls.part, part_name=cls.part.name, article="FLT-100", quantity=2, unit_price_rub=500)

    def stock(self, quantity=10):
        stock = StockItem.objects.create(part=self.part, unit_weight_g=100, location="A-01")
        adjust_stock(self.part.pk, quantity, "Начальная инвентаризация", self.user, uuid.uuid4())
        stock.refresh_from_db()
        return stock

    def purchase(self, quantity=5):
        purchase = PurchaseOrder.objects.create(supplier=self.supplier, created_by=self.user)
        line = PurchaseLine.objects.create(purchase=purchase, part=self.part, quantity=quantity, unit_cost_rub=Decimal("125.50"))
        return purchase, line

    def shipment(self, **overrides):
        values = dict(order=self.order, recipient_name="Тестовый получатель", recipient_phone="+79990000001",
                      city_label="Москва", city_code=44, tariff_code=136, delivery_point="MSK1", weight_g=500, length_cm=20, width_cm=15, height_cm=10)
        values.update(overrides)
        return Shipment.objects.create(**values)

    def packed(self):
        self.stock()
        process_order(self.order.pk, "reserve", self.user)
        process_order(self.order.pk, "pack", self.user)


class InventoryTests(WarehouseFixture):
    def test_supplier_text_is_not_inventory(self):
        self.assertFalse(StockItem.objects.exists())
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "reserve", self.user)
        self.assertFalse(StockMovement.objects.exists())
        self.assertFalse(Fulfillment.objects.exists())

    def test_adjustment_requires_note_and_cannot_go_negative(self):
        self.stock(3)
        with self.assertRaises(ValidationError):
            adjust_stock(self.part.pk, 1, "", self.user, uuid.uuid4())
        with self.assertRaises(ValidationError):
            adjust_stock(self.part.pk, -4, "Списание", self.user, uuid.uuid4())
        self.assertEqual(StockItem.objects.get(part=self.part).on_hand, 3)

    def test_adjustment_is_idempotent(self):
        key = uuid.uuid4()
        self.assertTrue(adjust_stock(self.part.pk, 5, "Приход", self.user, key))
        self.assertFalse(adjust_stock(self.part.pk, 5, "Приход", self.user, key))
        self.assertEqual(StockItem.objects.get(part=self.part).on_hand, 5)
        self.assertEqual(StockMovement.objects.count(), 1)

    def test_partial_receipt_full_receipt_and_duplicate(self):
        purchase, line = self.purchase()
        set_purchase_status(purchase.pk, "order", self.user)
        key = uuid.uuid4()
        receive_purchase(purchase.pk, line.pk, 2, self.user, key)
        self.assertFalse(receive_purchase(purchase.pk, line.pk, 2, self.user, key))
        purchase.refresh_from_db()
        self.assertEqual(purchase.status, "partial")
        self.assertEqual(StockItem.objects.get(part=self.part).on_hand, 2)
        receive_purchase(purchase.pk, line.pk, 3, self.user, uuid.uuid4())
        purchase.refresh_from_db()
        self.assertEqual(purchase.status, "received")
        self.assertEqual(StockItem.objects.get(part=self.part).on_hand, 5)
        self.assertEqual(StockMovement.objects.count(), 2)
        self.assertEqual(purchase.total, Decimal("627.50"))

    def test_cannot_receive_draft_cancelled_or_excess(self):
        purchase, line = self.purchase()
        with self.assertRaises(ValidationError):
            receive_purchase(purchase.pk, line.pk, 1, self.user, uuid.uuid4())
        set_purchase_status(purchase.pk, "order", self.user)
        with self.assertRaises(ValidationError):
            receive_purchase(purchase.pk, line.pk, 6, self.user, uuid.uuid4())
        set_purchase_status(purchase.pk, "cancel", self.user)
        with self.assertRaises(ValidationError):
            receive_purchase(purchase.pk, line.pk, 1, self.user, uuid.uuid4())
        self.assertFalse(StockMovement.objects.exists())

    def test_reservations_cannot_exceed_available_stock(self):
        stock = self.stock(3)
        process_order(self.order.pk, "reserve", self.user)
        stock.refresh_from_db()
        self.assertEqual((stock.on_hand, stock.reserved, stock.available), (3, 2, 1))
        with self.assertRaises(ValidationError):
            adjust_stock(self.part.pk, -2, "Списание", self.user, uuid.uuid4())
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "reserve", self.user)
        process_order(self.order.pk, "release", self.user)
        stock.refresh_from_db()
        self.assertEqual((stock.on_hand, stock.reserved), (3, 0))

    def test_multi_item_reservation_rolls_back_when_one_part_missing(self):
        self.stock()
        OrderItem.objects.create(order=self.order, part=self.part2, part_name=self.part2.name, quantity=1, unit_price_rub=5)
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "reserve", self.user)
        self.assertEqual(StockItem.objects.get(part=self.part).reserved, 0)
        self.assertEqual(StockMovement.objects.count(), 1)

    def test_unpaid_or_changed_order_cannot_be_packed(self):
        self.stock()
        self.order.status = Order.Status.CONFIRMED_BY_MANAGER
        self.order.save()
        process_order(self.order.pk, "reserve", self.user)
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "pack", self.user)
        self.order.status = Order.Status.PAID
        self.order.save()
        OrderItem.objects.filter(order=self.order).update(quantity=3)
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "pack", self.user)

    def test_dispatch_exactly_once_and_never_changes_payment_status(self):
        self.packed()
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "dispatch", self.user)
        self.shipment(mode="prod", cdek_number="123456", status="ready")
        process_order(self.order.pk, "dispatch", self.user)
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "dispatch", self.user)
        stock = StockItem.objects.get(part=self.part)
        self.assertEqual((stock.on_hand, stock.reserved), (8, 0))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")
        self.assertEqual(StockMovement.objects.filter(kind="dispatch").count(), 1)

    def test_test_shipment_cannot_dispatch_real_stock(self):
        self.packed()
        self.shipment(mode="test", status="ready", cdek_number="123456")
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "dispatch", self.user)

    def test_active_shipment_blocks_release(self):
        self.packed()
        shipment = self.shipment(status="submitting")
        with self.assertRaises(ValidationError):
            process_order(self.order.pk, "release", self.user)
        shipment.status = "cancelled"
        shipment.save()
        process_order(self.order.pk, "release", self.user)
        self.assertEqual(StockItem.objects.get(part=self.part).reserved, 0)

    def test_database_rejects_overreservation(self):
        stock = self.stock()
        with self.assertRaises(IntegrityError), transaction.atomic():
            StockItem.objects.filter(pk=stock.pk).update(reserved=11)


@override_settings(CDEK_ENABLED=True, CDEK_MODE="test", CDEK_CLIENT_ID="test-id", CDEK_CLIENT_SECRET="test-secret",
                   CDEK_SENDER_NAME="Тестовый отправитель", CDEK_SENDER_PHONE="+79990000002", CDEK_SENDER_CITY_CODE=44, CDEK_SENDER_ADDRESS="Тестовый адрес")
class CdekTests(WarehouseFixture):
    def test_disabled_and_wrong_environment_never_call_network(self):
        with override_settings(CDEK_ENABLED=False), self.assertRaises(ValidationError):
            cdek.CdekClient()
        with self.assertRaises(ValidationError):
            cdek.CdekClient("prod")

    def test_payload_uses_prepaid_items_and_exact_weights(self):
        self.packed()
        shipment = self.shipment()
        payload = cdek.shipment_payload(shipment)
        self.assertEqual(payload["number"], str(shipment.client_number))
        item = payload["packages"][0]["items"][0]
        self.assertEqual(item["payment"]["value"], 0)
        self.assertEqual((item["amount"], item["weight"], item["cost"]), (2, 100, 500))
        self.assertEqual(payload["delivery_point"], "MSK1")
        shipment.weight_g = 199
        with self.assertRaises(ValidationError):
            cdek.shipment_payload(shipment)

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_no_submission_without_paid_packed_order(self, request):
        shipment = self.shipment()
        with self.assertRaises(ValidationError):
            cdek.submit_shipment(shipment.pk, self.user)
        request.assert_not_called()
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "draft")

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_async_registration_and_no_duplicate_submission(self, request):
        self.packed()
        shipment = self.shipment()
        request.return_value = {"entity": {"uuid": str(uuid.uuid4())}, "requests": [{"state": "ACCEPTED"}]}
        cdek.submit_shipment(shipment.pk, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "accepted")
        self.assertEqual(shipment.cdek_number, "")
        with self.assertRaises(ValidationError):
            cdek.submit_shipment(shipment.pk, self.user)
        request.assert_called_once()

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_timeout_requires_reconciliation_not_retry(self, request):
        self.packed()
        shipment = self.shipment()
        request.side_effect = cdek.CdekError("Нет подтверждённого ответа")
        with self.assertRaises(ValidationError):
            cdek.submit_shipment(shipment.pk, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "submitting")
        with self.assertRaises(ValidationError):
            cdek.submit_shipment(shipment.pk, self.user)
        request.assert_called_once()
        request.side_effect = None
        request.return_value = {"entity": {"uuid": str(uuid.uuid4()), "number": str(shipment.client_number), "cdek_number": "123456789", "statuses": [{"code": "CREATED", "date_time": "2026-08-28T11:00:00+0300"}]}}
        cdek.sync_shipment(shipment.pk, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "ready")
        self.assertIn("im_number=", request.call_args.args[1])

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_status_uses_latest_event_and_keeps_payment_unchanged(self, request):
        shipment = self.shipment(status="accepted", mode="test", cdek_uuid=uuid.uuid4())
        request.return_value = {"entity": {"uuid": str(shipment.cdek_uuid), "number": str(shipment.client_number), "cdek_number": "123456789", "statuses": [
            {"code": "DELIVERED", "date_time": "2026-08-28T11:00:00+0300"},
            {"code": "CREATED", "date_time": "2026-08-27T11:00:00+0300"}]}}
        cdek.sync_shipment(shipment.pk, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "delivered")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_mismatched_carrier_response_rejected(self, request):
        shipment = self.shipment(status="submitting", mode="test")
        request.return_value = {"entity": {"uuid": str(uuid.uuid4()), "number": "another-order"}}
        with self.assertRaises(ValidationError):
            cdek.sync_shipment(shipment.pk, self.user)
        shipment.refresh_from_db()
        self.assertIsNone(shipment.cdek_uuid)

    def test_provider_error_never_exposes_recipient_or_secret(self):
        with self.assertRaises(ValidationError) as error:
            cdek.raise_provider_errors({"requests": [{"errors": [{"code": "recipient_error", "message": "Secret Customer +79990000001 test-secret"}]}]})
        self.assertIn("recipient_error", str(error.exception))
        self.assertNotIn("Secret Customer", str(error.exception))
        self.assertNotIn("test-secret", str(error.exception))

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_quote_and_label_contracts(self, request):
        shipment = self.shipment(mode="test")
        request.return_value = {"total_sum": 450.50, "period_min": 2, "period_max": 4}
        cdek.quote_shipment(shipment, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.quoted_price, Decimal("450.50"))
        shipment.cdek_uuid, shipment.cdek_number, shipment.status = uuid.uuid4(), "12345", "ready"
        shipment.save()
        label_id = uuid.uuid4()
        request.return_value = {"entity": {"uuid": str(label_id)}}
        cdek.prepare_label(shipment, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.label_uuid, label_id)
        request.return_value = b"%PDF-1.7\nfixture"
        self.assertTrue(cdek.download_label(shipment).startswith(b"%PDF"))
        self.assertEqual(request.call_args.args[1], f"/print/orders/{label_id}.pdf")

    def test_shipment_form_rejects_bad_destination_and_dimensions(self):
        form = ShipmentForm(data={"recipient_name": "Тест", "recipient_phone": "bad", "city_label": "Москва", "city_code": 0, "tariff_code": 136,
                                  "delivery_point": "", "weight_g": 0, "length_cm": 0, "width_cm": 10, "height_cm": 10})
        self.assertFalse(form.is_valid())
        for field in ["recipient_phone", "city_code", "delivery_point", "weight_g", "length_cm"]:
            self.assertIn(field, form.errors)

    @patch("apps.warehouse.cdek.build_opener")
    def test_transport_keeps_credentials_in_post_body(self, opener):
        import json
        from unittest.mock import MagicMock
        auth, response = MagicMock(), MagicMock()
        auth.__enter__.return_value.read.return_value = json.dumps({"access_token": "test-token"}).encode()
        response.__enter__.return_value.read.return_value = b'{"entity": {}}'
        opener.return_value.open.side_effect = [auth, response]
        cdek.CdekClient().request("GET", "/orders/test")
        first = opener.return_value.open.call_args_list[0].args[0]
        self.assertEqual(first.full_url, "https://api.edu.cdek.ru/v2/oauth/token")
        self.assertNotIn("test-secret", first.full_url)
        self.assertIn(b"client_secret=test-secret", first.data)
        second = opener.return_value.open.call_args_list[1].args[0]
        self.assertEqual(second.get_header("Authorization"), "Bearer test-token")

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_deleted_final_status_is_ignored(self, request):
        shipment = self.shipment(status="accepted", mode="test", cdek_uuid=uuid.uuid4())
        request.return_value = {"entity": {"uuid": str(shipment.cdek_uuid), "number": str(shipment.client_number), "cdek_number": "123", "statuses": [
            {"code": "DELIVERED", "date_time": "2026-08-28T11:00:00+0300", "deleted": True},
            {"code": "TAKEN_BY_COURIER", "date_time": "2026-08-28T10:00:00+0300"}]}}
        cdek.sync_shipment(shipment.pk, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "transit")

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_not_delivered_requires_attention_without_stock_return(self, request):
        self.packed()
        shipment = self.shipment(status="accepted", mode="test", cdek_uuid=uuid.uuid4())
        request.return_value = {"entity": {"uuid": str(shipment.cdek_uuid), "number": str(shipment.client_number), "cdek_number": "123", "statuses": [
            {"code": "NOT_DELIVERED", "date_time": "2026-08-28T11:00:00+0300"}]}}
        cdek.sync_shipment(shipment.pk, self.user)
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "error")
        self.assertEqual(StockItem.objects.get(part=self.part).on_hand, 10)

    @patch("apps.warehouse.cdek.CdekClient.request")
    def test_disabled_scheduler_never_contacts_cdek(self, request):
        self.shipment(status="submitting", mode="test")
        with override_settings(CDEK_ENABLED=False):
            call_command("sync_cdek_shipments", verbosity=0)
        request.assert_not_called()


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class WorkspaceViewsTests(WarehouseFixture):
    def setUp(self):
        self.client.force_login(self.user)

    def test_all_pages_render_and_get_never_creates_stock(self):
        purchase, _ = self.purchase()
        shipment = self.shipment()
        routes = ["/admin/", "/admin/warehouse/", "/admin/warehouse/parts/", "/admin/warehouse/parts/new/",
                  f"/admin/warehouse/parts/{self.part.pk}/", "/admin/warehouse/purchases/", "/admin/warehouse/purchases/new/",
                  f"/admin/warehouse/purchases/{purchase.pk}/", "/admin/warehouse/orders/", f"/admin/warehouse/orders/{self.order.pk}/",
                  "/admin/warehouse/shipments/", f"/admin/warehouse/shipments/order/{shipment.order_id}/", "/admin/warehouse/activity/"]
        for url in routes:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                if url != "/admin/":
                    self.assertIn("no-store", response["Cache-Control"])
                    self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
                self.assertNotContains(response, "test-secret")
        self.assertFalse(StockItem.objects.exists())
        self.assertFalse(Fulfillment.objects.exists())

    def test_workspace_and_django_admin_share_brand_and_theme_controls(self):
        workspace = self.client.get("/admin/warehouse/")
        self.assertContains(workspace, "warehouse/theme.js")
        self.assertContains(workspace, "data-theme-toggle")

        admin_index = self.client.get("/admin/")
        self.assertContains(admin_index, "warehouse/admin.css")
        self.assertContains(admin_index, "warehouse/theme.js")
        self.assertContains(admin_index, "zemazap-admin-brand")
        self.assertContains(admin_index, "data-theme-toggle")

        superuser = get_user_model().objects.create_superuser("theme-admin", password="test-only")
        self.client.force_login(superuser)
        changelist = self.client.get("/admin/leads/customerrequest/")
        self.assertEqual(changelist.status_code, 200)
        self.assertContains(changelist, "warehouse/admin.css")
        self.assertContains(changelist, "Центр управления")
        self.assertContains(changelist, "data-theme-toggle")

    def test_anonymous_and_unprivileged_staff_denied(self):
        self.client.logout()
        response = self.client.get("/admin/warehouse/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
        user = get_user_model().objects.create_user("unprivileged", is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.get("/admin/warehouse/").status_code, 403)

    def test_owner_dashboard_is_primary_for_owner_but_not_warehouse_role(self):
        self.client.logout()
        response = self.client.get("/admin/owner/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
        self.assertIn("next=/admin/owner/", response["Location"])

        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/admin/owner/").status_code, 403)

        owner = get_user_model().objects.create_user("owner-test", is_staff=True)
        owner.groups.add(Group.objects.get(name="owner"))
        self.client.force_login(owner)
        with override_settings(ZEMAZAP_SITE_URL="http://storefront.example:3000"):
            response = self.client.get("/admin/owner/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Центр управления")
        self.assertContains(response, "Заявки, деньги, остатки и доставка на одном экране.")
        self.assertContains(response, 'href="http://storefront.example:3000/"', count=2)
        self.assertEqual(response.context["paid_to_fulfill_count"], 1)
        self.assertEqual(response.context["untracked_stock_count"], 2)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

        superuser = get_user_model().objects.create_superuser("owner-superuser", password="test-only")
        self.client.force_login(superuser)
        self.assertEqual(self.client.get("/admin/owner/").status_code, 200)

    def test_admin_root_redirects_owner_after_login_and_preserves_future_staff_access(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Склад Zemazap")

        superuser = get_user_model().objects.create_superuser("root-redirect-test", password="test-only")
        self.client.logout()
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

        response = self.client.post(
            "/admin/login/",
            {"username": superuser.username, "password": "test-only", "next": "/admin/"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [("/admin/", 302), ("/admin/owner/", 302)])
        self.assertContains(response, "Центр управления")

    def test_inventory_viewer_cannot_see_order_pii_or_mutate(self):
        user = get_user_model().objects.create_user("inventory-viewer", is_staff=True)
        user.user_permissions.add(Permission.objects.get(codename="view_stockitem"))
        self.client.force_login(user)
        self.assertEqual(self.client.get("/admin/warehouse/").status_code, 200)
        self.assertEqual(self.client.get("/admin/warehouse/orders/").status_code, 403)
        self.assertEqual(self.client.post(reverse("warehouse:part-adjust", args=[self.part.pk]), {"quantity": 5, "note": "Test", "key": uuid.uuid4()}).status_code, 403)
        self.assertFalse(StockItem.objects.exists())

    def test_csrf_is_enforced_for_operational_posts(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(reverse("warehouse:part-adjust", args=[self.part.pk]), {"quantity": 5, "note": "Test", "key": uuid.uuid4()})
        self.assertEqual(response.status_code, 403)

    def test_mutation_endpoint_rejects_get(self):
        response = self.client.get(reverse("warehouse:part-adjust", args=[self.part.pk]))
        self.assertEqual(response.status_code, 405)

    def test_part_edit_preserves_balance_and_updates_catalog_search(self):
        self.stock()
        process_order(self.order.pk, "reserve", self.user)
        response = self.client.post(reverse("warehouse:part", args=[self.part.pk]), {
            "name": "Новый фильтр", "primary_article": "FLT-NEW", "primary_oem": "OEM-NEW", "brand": self.part.brand_id,
            "category": self.part.category_id, "manufacturer": self.part.manufacturer_id, "condition": "новая", "is_active": "on",
            "stock-location": "B-02", "stock-minimum": 5, "stock-unit_weight_g": 150, "stock-on_hand": 999,
            "offer-supplier": self.supplier.pk, "offer-price_rub": 600, "offer-availability": "в наличии", "offer-delivery": "Со склада",
        })
        self.assertEqual(response.status_code, 302)
        self.part.refresh_from_db()
        self.assertIn("flt-new", self.part.search_text)
        stock = StockItem.objects.get(part=self.part)
        self.assertEqual((stock.on_hand, stock.reserved, stock.location), (10, 2, "B-02"))
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.price_rub, 600)
        self.assertEqual(OrderItem.objects.get(order=self.order).unit_price_rub, 500)

    def test_purchase_create_and_receive_through_pages(self):
        response = self.client.post(reverse("warehouse:purchase-new"), {
            "supplier": self.supplier.pk, "reference": "INV-1", "lines-TOTAL_FORMS": 1, "lines-INITIAL_FORMS": 0,
            "lines-MIN_NUM_FORMS": 1, "lines-MAX_NUM_FORMS": 50, "lines-0-part": self.part.pk,
            "lines-0-quantity": 5, "lines-0-unit_cost_rub": "125.50",
        })
        self.assertEqual(response.status_code, 302)
        purchase = PurchaseOrder.objects.get()
        self.client.post(reverse("warehouse:purchase-action", args=[purchase.pk]), {"action": "order"})
        line = purchase.lines.get()
        payload = {"action": "receive", "line_id": line.pk, "quantity": 3, "key": str(uuid.uuid4())}
        self.client.post(reverse("warehouse:purchase-action", args=[purchase.pk]), payload)
        self.client.post(reverse("warehouse:purchase-action", args=[purchase.pk]), payload)
        self.assertEqual(StockItem.objects.get(part=self.part).on_hand, 3)

    def test_search_filters_and_pagination(self):
        self.stock(1)
        response = self.client.get("/admin/warehouse/parts/?q=FLT-100&status=low")
        self.assertEqual(response.context["page"].paginator.count, 0)
        response = self.client.get("/admin/warehouse/parts/?status=untracked&page=99999")
        self.assertContains(response, self.part2.name)
        self.assertNotContains(response, self.part.name)

    @patch("apps.warehouse.cdek.submit_shipment")
    def test_carrier_submission_requires_explicit_confirmation(self, submit):
        shipment = self.shipment()
        self.client.post(reverse("warehouse:shipment-action", args=[shipment.pk]), {"action": "submit"})
        submit.assert_not_called()
        self.client.post(reverse("warehouse:shipment-action", args=[shipment.pk]), {"action": "submit", "confirm": "on"})
        submit.assert_called_once_with(shipment.pk, self.user)

    def test_native_admin_cannot_bypass_stock_services(self):
        stock = self.stock()
        response = self.client.post(f"/admin/warehouse/stockitem/{stock.pk}/change/", {"on_hand": 999})
        self.assertEqual(response.status_code, 403)
        stock.refresh_from_db()
        self.assertEqual(stock.on_hand, 10)

    def test_role_bootstrap_idempotent_and_does_not_grant_financial_authority(self):
        before = Group.objects.get(name="warehouse_manager").permissions.count()
        call_command("bootstrap_roles", verbosity=0)
        self.assertEqual(Group.objects.get(name="warehouse_manager").permissions.count(), before)
        self.assertFalse(self.user.has_perm("payments.create_payment_link"))
        self.assertFalse(self.user.has_perm("refunds.process_refund"))
        self.assertFalse(self.user.has_perm("auth.change_user"))
