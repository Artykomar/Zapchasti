from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from apps.payments.services import create_payment_link_for_order

from .models import Order, OrderComment, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("created_at",)


class OrderCommentInline(admin.TabularInline):
    model = OrderComment
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "status", "total_amount_rub", "currency", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("=id", "token", "customer_name", "contact", "items__article", "items__part_name")
    readonly_fields = ("token", "created_at", "updated_at", "confirmed_at")
    inlines = [OrderItemInline, OrderStatusHistoryInline, OrderCommentInline]
    actions = ["mark_confirmed", "create_payment_links"]

    def get_list_display(self, request):
        if request.user.has_perm("orders.view_order_pii") or request.user.is_superuser:
            return super().get_list_display(request)
        return ("id", "masked_customer", "status", "total_amount_rub", "currency", "created_at")

    def get_search_fields(self, request):
        if request.user.has_perm("orders.view_order_pii") or request.user.is_superuser:
            return super().get_search_fields(request)
        return ("=id", "token", "items__article", "items__part_name")

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or [])
        if not request.user.has_perm("orders.view_order_pii") and not request.user.is_superuser:
            excluded.extend(["request", "customer_name", "contact", "vehicle", "manager_note"])
        return excluded

    @admin.display(description="customer")
    def masked_customer(self, obj):
        return f"Клиент заказа #{obj.pk}"

    @admin.action(description="Mark selected orders as confirmed by manager")
    def mark_confirmed(self, request, queryset):
        updated = 0
        for order in queryset:
            if order.status == Order.Status.DRAFT:
                order.mark_confirmed(note=f"Confirmed by {request.user}.")
                updated += 1
        self.message_user(request, f"Confirmed {updated} order(s).", messages.SUCCESS)

    def has_create_payment_link_permission(self, request):
        return request.user.has_perm("payments.create_payment_link")

    @admin.action(description="Create payment links for selected orders", permissions=["create_payment_link"])
    def create_payment_links(self, request, queryset):
        created = 0
        errors = []
        for order in queryset:
            try:
                create_payment_link_for_order(order)
                created += 1
            except ValidationError as exc:
                errors.append(f"#{order.pk}: {'; '.join(exc.messages)}")
        if created:
            self.message_user(request, f"Payment links ready: {created}.", messages.SUCCESS)
        if errors:
            self.message_user(request, " ".join(errors[:10]), messages.ERROR)
