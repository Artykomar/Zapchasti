from __future__ import annotations

import json
import logging
from urllib import request as urllib_request

from django.conf import settings
from django.core.mail import send_mail

from apps.leads.models import CustomerRequest

logger = logging.getLogger(__name__)


def build_request_notification_text(customer_request: CustomerRequest) -> str:
    items = customer_request.items.all()
    item_lines = [
        f"- {item.part_name}{', арт. ' + item.article if item.article else ''}, {item.quantity} шт."
        for item in items
    ] or ["- подбор по описанию"]
    base_url = getattr(settings, "ZEMAZAP_SITE_URL", "http://127.0.0.1:3000").rstrip("/")
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
            f"Открыть в Django admin: {base_url}/admin/leads/customerrequest/{customer_request.id}/change/",
        ]
    )


def notify_manager_about_request(customer_request: CustomerRequest) -> None:
    text = build_request_notification_text(customer_request)
    subject = f"Новая заявка Zemazap: {customer_request.customer_name}"
    manager_email = getattr(settings, "ZEMAZAP_MANAGER_EMAIL", "")

    if manager_email:
        try:
            send_mail(subject, text, None, [manager_email], fail_silently=False)
        except Exception:
            logger.exception("Email manager notification failed")

    token = getattr(settings, "ZEMAZAP_TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "ZEMAZAP_TELEGRAM_CHAT_ID", "")

    if token and chat_id:
        try:
            payload = json.dumps({"chat_id": chat_id, "text": text, "disable_web_page_preview": True}).encode("utf-8")
            req = urllib_request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib_request.urlopen(req, timeout=10).read()
        except Exception:
            logger.exception("Telegram manager notification failed")
