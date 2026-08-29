from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import PurchaseOrder, Shipment, StockItem, StockMovement, WarehouseEvent


class ReadOnlyWarehouseAdmin(admin.ModelAdmin):
    """Operational writes must use the transactional workspace, never raw admin forms."""
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StockItem)
class StockItemAdmin(ReadOnlyWarehouseAdmin):
    list_display = ("part", "location", "on_hand", "reserved", "minimum", "workspace_link")
    search_fields = ("part__name", "part__primary_article", "location")
    list_select_related = ("part",)

    @admin.display(description="Склад")
    def workspace_link(self, obj):
        return format_html('<a href="{}">Открыть карточку</a>', reverse("warehouse:part", args=[obj.part_id]))


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ReadOnlyWarehouseAdmin):
    list_display = ("id", "supplier", "status", "expected_at", "created_at")
    list_filter = ("status",)
    search_fields = ("reference", "supplier__name")
    list_select_related = ("supplier",)


@admin.register(Shipment)
class ShipmentAdmin(ReadOnlyWarehouseAdmin):
    list_display = ("order_id", "status", "cdek_number", "mode", "last_synced_at")
    list_filter = ("status", "mode")
    search_fields = ("cdek_number", "client_number")

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj) and request.user.has_perm("orders.view_order_pii")


@admin.register(StockMovement)
class StockMovementAdmin(ReadOnlyWarehouseAdmin):
    list_display = ("created_at", "stock", "kind", "quantity", "reserved_delta", "balance_after", "actor")
    list_filter = ("kind",)
    list_select_related = ("stock__part", "actor")


@admin.register(WarehouseEvent)
class WarehouseEventAdmin(ReadOnlyWarehouseAdmin):
    list_display = ("created_at", "actor", "action", "target")
    list_select_related = ("actor",)
