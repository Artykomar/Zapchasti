from django.contrib import admin

from .models import NotificationSettings


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ("manager_email", "telegram_chat_id", "telegram_bot_token_configured", "updated_at")

# Register your models here.
