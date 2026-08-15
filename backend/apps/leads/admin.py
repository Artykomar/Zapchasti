from django.contrib import admin

from apps.orders.services import create_order_from_request

from .models import CustomerRequest, CustomerRequestEvent, CustomerRequestItem


class CustomerRequestItemInline(admin.TabularInline):
    model = CustomerRequestItem
    extra = 0


class CustomerRequestEventInline(admin.TabularInline):
    model = CustomerRequestEvent
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(CustomerRequest)
class CustomerRequestAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "contact", "status", "source", "privacy_consent_version", "total_estimate_rub", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("customer_name", "contact", "vehicle", "request_text", "items__article", "items__part_name")
    readonly_fields = (
        "privacy_policy_version",
        "privacy_consent_version",
        "consent_accepted_at",
        "consent_source",
        "consent_ip",
        "consent_user_agent",
    )
    inlines = [CustomerRequestItemInline, CustomerRequestEventInline]
    actions = ["create_orders"]

    @admin.action(description="Create draft order from selected requests")
    def create_orders(self, request, queryset):
        created = 0
        skipped = 0
        for customer_request in queryset:
            _order, was_created = create_order_from_request(
                customer_request,
                note=f"Created from CustomerRequest admin action by {request.user}.",
            )
            if was_created:
                created += 1
            else:
                skipped += 1
        self.message_user(request, f"Created {created} order(s), skipped {skipped} existing order(s).")

# Register your models here.
