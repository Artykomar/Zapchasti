from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "contact", "normalized_contact", "updated_at")
    search_fields = ("display_name", "contact", "normalized_contact")

    def get_list_display(self, request):
        if request.user.has_perm("customers.view_customer_pii") or request.user.is_superuser:
            return super().get_list_display(request)
        return ("masked_name", "masked_contact", "updated_at")

    def get_search_fields(self, request):
        if request.user.has_perm("customers.view_customer_pii") or request.user.is_superuser:
            return super().get_search_fields(request)
        return ()

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or [])
        if not request.user.has_perm("customers.view_customer_pii") and not request.user.is_superuser:
            excluded.extend(["display_name", "contact", "normalized_contact"])
        return excluded

    @admin.display(description="customer")
    def masked_name(self, obj):
        return f"Клиент #{obj.pk}"

    @admin.display(description="contact")
    def masked_contact(self, obj):
        digits = "".join(character for character in obj.contact if character.isdigit())
        return f"***{digits[-4:]}" if len(digits) >= 4 else "***"

# Register your models here.
