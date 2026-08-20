from django.contrib import admin

from .models import NotificationDelivery, NotificationSettings


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ("manager_email", "telegram_chat_id", "telegram_bot_token_configured", "updated_at")


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "channel", "template_code", "status", "object_type", "object_id", "attempt_count", "created_at")
    list_filter = ("channel", "template_code", "status", "created_at")
    search_fields = ("=id", "template_code", "object_type", "=object_id", "recipient_hint")
    readonly_fields = (
        "channel",
        "template_code",
        "object_type",
        "object_id",
        "recipient_hint",
        "safe_payload",
        "attempt_count",
        "last_error_code",
        "sent_at",
        "created_at",
        "updated_at",
    )

# Register your models here.
