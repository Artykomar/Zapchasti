from django.contrib import admin

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
    list_display = ("customer_name", "contact", "status", "source", "total_estimate_rub", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("customer_name", "contact", "vehicle", "request_text", "items__article", "items__part_name")
    inlines = [CustomerRequestItemInline, CustomerRequestEventInline]

# Register your models here.
