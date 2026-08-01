from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "contact", "normalized_contact", "updated_at")
    search_fields = ("display_name", "contact", "normalized_contact")

# Register your models here.
