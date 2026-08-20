import csv

from django.contrib import admin, messages
from django.http import HttpResponse

from apps.orders.services import create_order_from_request

from .models import CustomerRequest, CustomerRequestEvent, CustomerRequestItem
from .services import anonymize_customer_request


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
    actions = ["create_orders", "export_personal_data", "anonymize_personal_data"]

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.has_perm("leads.view_request_pii") and not request.user.is_superuser:
            fields[0] = "masked_customer"
            fields[1] = "masked_contact"
        return fields

    @admin.display(description="customer")
    def masked_customer(self, obj):
        return f"Клиент заявки #{obj.pk}"

    def get_search_fields(self, request):
        if request.user.has_perm("leads.view_request_pii") or request.user.is_superuser:
            return super().get_search_fields(request)
        return ("=id", "items__article", "items__part_name")

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or [])
        if not request.user.has_perm("leads.view_request_pii") and not request.user.is_superuser:
            excluded.extend(
                ["customer", "customer_name", "contact", "vehicle", "request_text", "consent_ip", "consent_user_agent"]
            )
        return excluded

    @admin.display(description="contact")
    def masked_contact(self, obj):
        digits = "".join(character for character in obj.contact if character.isdigit())
        return f"***{digits[-4:]}" if len(digits) >= 4 else "***"

    @admin.action(description="Export selected requests as CSV")
    def export_personal_data(self, request, queryset):
        if not request.user.has_perm("leads.export_request_pii") and not request.user.is_superuser:
            self.message_user(request, "Недостаточно прав для выгрузки ПДн.", messages.ERROR)
            return None
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="zemazap-requests.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(["id", "name", "contact", "vehicle", "request", "status", "created_at"])
        for item in queryset.order_by("id"):
            writer.writerow(
                [item.id, item.customer_name, item.contact, item.vehicle, item.request_text, item.status, item.created_at]
            )
        return response

    @admin.action(description="Anonymize personal data in selected requests")
    def anonymize_personal_data(self, request, queryset):
        if not request.user.has_perm("leads.anonymize_request_pii") and not request.user.is_superuser:
            self.message_user(request, "Недостаточно прав для анонимизации ПДн.", messages.ERROR)
            return
        updated = 0
        for customer_request in queryset:
            if not customer_request.anonymized_at:
                anonymize_customer_request(customer_request, reason=f"Admin action by {request.user}.")
                updated += 1
        self.message_user(request, f"Анонимизировано заявок: {updated}.", messages.SUCCESS)

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
