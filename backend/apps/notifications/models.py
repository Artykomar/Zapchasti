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


class NotificationDelivery(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", "email"
        TELEGRAM = "telegram", "telegram"
        MAX = "max", "MAX"
        ADMIN = "admin", "admin"

    class Status(models.TextChoices):
        PENDING = "pending", "pending"
        SENT = "sent", "sent"
        FAILED = "failed", "failed"
        SKIPPED = "skipped", "skipped"

    channel = models.CharField(max_length=20, choices=Channel.choices)
    template_code = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    object_type = models.CharField(max_length=80)
    object_id = models.PositiveIntegerField()
    recipient_hint = models.CharField(max_length=160, blank=True)
    safe_payload = models.JSONField(default=dict, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    last_error_code = models.CharField(max_length=160, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "next_attempt_at"]),
            models.Index(fields=["object_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.channel}:{self.template_code}:{self.status}"

# Create your models here.
