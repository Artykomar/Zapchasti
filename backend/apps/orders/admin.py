from django.contrib import admin, messages

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
    actions = ["mark_confirmed"]

    @admin.action(description="Mark selected orders as confirmed by manager")
    def mark_confirmed(self, request, queryset):
        updated = 0
        for order in queryset:
            if order.status == Order.Status.DRAFT:
                order.mark_confirmed(note=f"Confirmed by {request.user}.")
                updated += 1
        self.message_user(request, f"Confirmed {updated} order(s).", messages.SUCCESS)
