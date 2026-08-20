from __future__ import annotations

import json
import logging
from datetime import timedelta
from urllib import request as urllib_request

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from apps.leads.models import CustomerRequest

from .models import NotificationDelivery

logger = logging.getLogger(__name__)


def mask_contact(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    if len(digits) >= 4:
        return f"***{digits[-4:]}"
    return "***"


def build_request_notification_text(customer_request: CustomerRequest, include_pii: bool = True) -> str:
    items = customer_request.items.all()
    item_lines = [
        f"- {item.part_name}{', арт. ' + item.article if item.article else ''}, {item.quantity} шт."
        for item in items
    ] or ["- подбор по описанию"]
    base_url = getattr(settings, "ZEMAZAP_SITE_URL", "http://127.0.0.1:3000").rstrip("/")
    admin_url = f"{base_url}/admin/leads/customerrequest/{customer_request.id}/change/"
    if not include_pii:
        return "\n".join(
            [
                f"Новая заявка Zemazap #{customer_request.id}",
                "",
                f"Источник: {'корзина' if customer_request.source == 'cart' else 'форма подбора'}",
                f"Контакт: {mask_contact(customer_request.contact)}",
                f"Позиций: {items.count()}",
                "",
                f"Открыть в Django admin: {admin_url}",
            ]
        )

    return "\n".join(
        [
            "Новая заявка Zemazap",
            "",
            f"Клиент: {customer_request.customer_name}",
            f"Контакт: {customer_request.contact}",
            f"Автомобиль: {customer_request.vehicle}" if customer_request.vehicle else "",
            f"Запрос: {customer_request.request_text}" if customer_request.request_text else "",
            f"Источник: {'корзина' if customer_request.source == 'cart' else 'форма подбора'}",
            f"Сумма: {customer_request.total_estimate_rub or 'уточняется'}",
            "",
            "Позиции:",
            *item_lines,
            "",
            f"Открыть в Django admin: {admin_url}",
        ]
    )


def _delivery_for_request(customer_request: CustomerRequest, channel: str, recipient_hint: str) -> NotificationDelivery:
    return NotificationDelivery.objects.create(
        channel=channel,
        template_code="new_customer_request",
        object_type="leads.CustomerRequest",
        object_id=customer_request.pk,
        recipient_hint=recipient_hint,
        safe_payload={"request_id": customer_request.pk, "source": customer_request.source},
    )


def _load_request(delivery: NotificationDelivery) -> CustomerRequest:
    if delivery.object_type != "leads.CustomerRequest":
        raise ValueError("Unsupported notification object type.")
    return CustomerRequest.objects.get(pk=delivery.object_id)


@transaction.atomic
def deliver_notification(delivery: NotificationDelivery) -> NotificationDelivery:
    delivery = NotificationDelivery.objects.select_for_update().get(pk=delivery.pk)
    if delivery.status == NotificationDelivery.Status.SENT:
        return delivery
    delivery.attempt_count += 1
    customer_request = _load_request(delivery)

    try:
        if delivery.channel == NotificationDelivery.Channel.EMAIL:
            recipient = getattr(settings, "ZEMAZAP_MANAGER_EMAIL", "")
            if not recipient:
                delivery.status = NotificationDelivery.Status.SKIPPED
            else:
                text = build_request_notification_text(customer_request, include_pii=True)
                send_mail(
                    f"Новая заявка Zemazap #{customer_request.pk}",
                    text,
                    None,
                    [recipient],
                    fail_silently=False,
                )
                delivery.status = NotificationDelivery.Status.SENT
        elif delivery.channel == NotificationDelivery.Channel.TELEGRAM:
            token = getattr(settings, "ZEMAZAP_TELEGRAM_BOT_TOKEN", "")
            chat_id = getattr(settings, "ZEMAZAP_TELEGRAM_CHAT_ID", "")
            if not token or not chat_id:
                delivery.status = NotificationDelivery.Status.SKIPPED
            else:
                text = build_request_notification_text(
                    customer_request,
                    include_pii=getattr(settings, "PII_IN_NOTIFICATIONS_ALLOWED", False),
                )
                payload = json.dumps(
                    {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
                ).encode("utf-8")
                request = urllib_request.Request(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                urllib_request.urlopen(request, timeout=10).read()
                delivery.status = NotificationDelivery.Status.SENT
        else:
            delivery.status = NotificationDelivery.Status.SKIPPED
    except Exception as exc:
        delivery.status = NotificationDelivery.Status.FAILED
        delivery.last_error_code = exc.__class__.__name__[:160]
        delay_minutes = min(60, 2 ** min(delivery.attempt_count, 5))
        delivery.next_attempt_at = timezone.now() + timedelta(minutes=delay_minutes)
        logger.warning(
            "Notification delivery failed",
            extra={"delivery_id": delivery.pk, "channel": delivery.channel, "error_code": delivery.last_error_code},
        )
    else:
        delivery.last_error_code = ""
        delivery.next_attempt_at = None
        if delivery.status == NotificationDelivery.Status.SENT:
            delivery.sent_at = timezone.now()

    delivery.save(
        update_fields=[
            "attempt_count",
            "status",
            "last_error_code",
            "next_attempt_at",
            "sent_at",
            "updated_at",
        ]
    )
    return delivery


def notify_manager_about_request(customer_request: CustomerRequest) -> None:
    deliveries = []
    manager_email = getattr(settings, "ZEMAZAP_MANAGER_EMAIL", "")
    if manager_email:
        deliveries.append(
            _delivery_for_request(customer_request, NotificationDelivery.Channel.EMAIL, "manager-email")
        )
    if getattr(settings, "ZEMAZAP_TELEGRAM_BOT_TOKEN", "") and getattr(
        settings, "ZEMAZAP_TELEGRAM_CHAT_ID", ""
    ):
        deliveries.append(
            _delivery_for_request(customer_request, NotificationDelivery.Channel.TELEGRAM, "manager-telegram")
        )
    for delivery in deliveries:
        deliver_notification(delivery)
