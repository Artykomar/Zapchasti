from django.db import models


class NotificationSettings(models.Model):
    manager_email = models.EmailField(blank=True)
    telegram_chat_id = models.CharField(max_length=120, blank=True)
    telegram_bot_token_configured = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "notification settings"

    def __str__(self) -> str:
        return "notification settings"

# Create your models here.
