from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from django.conf import settings


class PaymentProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class RegisteredPayment:
    bank_order_id: str
    form_url: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class ProviderPaymentStatus:
    order_status: int
    order_number: str
    amount_minor: int | None
    deposited_amount_minor: int | None
    refunded_amount_minor: int | None
    currency: str
    raw: dict[str, Any]


def _minor_units(amount_rub: int) -> int:
    return int(Decimal(amount_rub) * 100)


def _tax_type(vat_label: str) -> int:
    normalized = vat_label.strip().lower().replace(" ", "")
    if "безндс" in normalized:
        return 0
    if "20/120" in normalized:
        return 7
    if "20" in normalized:
        return 6
    if "10/110" in normalized:
        return 4
    if "10" in normalized:
        return 2
    if "0%" in normalized or "ндс0" in normalized:
        return 1
    return 0


def _payment_method_code(value: str) -> str:
    return {
        "full_prepayment": "1",
        "partial_prepayment": "2",
        "advance": "3",
        "full_payment": "4",
        "partial_payment": "5",
        "credit": "6",
        "credit_payment": "7",
    }.get(value, "4")


def _payment_subject_code(value: str) -> str:
    return {
        "commodity": "1",
        "excise": "2",
        "job": "3",
        "service": "4",
        "gambling_bet": "5",
        "gambling_prize": "6",
        "lottery": "7",
        "lottery_prize": "8",
        "intellectual_activity": "9",
        "payment": "10",
        "agent_commission": "11",
        "composite": "12",
        "other": "13",
    }.get(value, "1")


def build_alfa_order_bundle(order) -> dict[str, Any]:
    items = []
    for position, item in enumerate(order.items.all(), start=1):
        price_minor = _minor_units(item.unit_price_rub)
        amount_minor = _minor_units(item.line_total_rub)
        items.append(
            {
                "positionId": str(position),
                "name": (item.fiscal_name or item.part_name)[:128],
                "quantity": {"value": item.quantity, "measure": item.unit or "шт."},
                "itemAmount": amount_minor,
                "itemCode": (item.article or f"order-{order.pk}-item-{item.pk}")[:100],
                "itemPrice": price_minor,
                "tax": {"taxType": _tax_type(item.vat_label)},
                "itemDetails": {
                    "itemDetailsParams": [
                        {"name": "paymentMethod", "value": _payment_method_code(item.payment_method), "type": "1"},
                        {"name": "paymentObject", "value": _payment_subject_code(item.payment_subject), "type": "1"},
                    ]
                },
            }
        )
    return {"cartItems": {"items": items}}


def sanitize_provider_payload(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "errorCode",
        "errorMessage",
        "orderStatus",
        "orderNumber",
        "amount",
        "currency",
        "actionCode",
        "actionCodeDescription",
    }
    sanitized = {key: payload[key] for key in allowed if key in payload}
    payment_amount_info = payload.get("paymentAmountInfo")
    if isinstance(payment_amount_info, dict):
        sanitized["paymentAmountInfo"] = {
            key: payment_amount_info[key]
            for key in ("approvedAmount", "depositedAmount", "refundedAmount", "paymentState", "totalAmount")
            if key in payment_amount_info
        }
    return sanitized


class AlfaBankClient:
    def __init__(self):
        self.gateway_url = str(getattr(settings, "ALFA_BANK_GATEWAY_URL", "")).rstrip("/")
        self.username = str(getattr(settings, "ALFA_BANK_USERNAME", ""))
        self.password = str(getattr(settings, "ALFA_BANK_PASSWORD", ""))
        self.token = str(getattr(settings, "ALFA_BANK_TOKEN", ""))
        self.timeout = int(getattr(settings, "ALFA_BANK_TIMEOUT_SECONDS", 15))
        if not self.gateway_url:
            raise PaymentProviderError("ALFA_BANK_GATEWAY_URL is not configured.")
        if not self.token and not (self.username and self.password):
            raise PaymentProviderError("Alfa-Bank API credentials are not configured.")

    def _auth(self) -> dict[str, str]:
        if self.token:
            return {"token": self.token}
        return {"userName": self.username, "password": self.password}

    def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.gateway_url}/{method}.do"
        encoded = urllib_parse.urlencode({**self._auth(), **payload}).encode("utf-8")
        request = urllib_request.Request(
            url,
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            raise PaymentProviderError(f"Alfa-Bank gateway request failed: {exc}") from exc
        error_code = str(result.get("errorCode", "0"))
        if error_code not in {"", "0"}:
            raise PaymentProviderError(
                f"Alfa-Bank gateway rejected the request ({error_code}): {result.get('errorMessage', 'unknown error')}"
            )
        return result

    def register(self, payment) -> RegisteredPayment:
        order = payment.order
        site_url = str(getattr(settings, "ZEMAZAP_SITE_URL", "")).rstrip("/")
        payload: dict[str, Any] = {
            "orderNumber": payment.provider_order_number,
            "amount": _minor_units(payment.amount_rub),
            "currency": "643",
            "returnUrl": f"{site_url}/payment/success?order={order.token}",
            "failUrl": f"{site_url}/payment/fail?order={order.token}",
            "description": f"Заказ Zemazap #{order.pk}",
            "language": "ru",
        }
        if getattr(settings, "FISCALIZATION_ENABLED", False) and getattr(
            settings, "FISCAL_PROVIDER", "mock"
        ) == "alfa":
            payload["orderBundle"] = json.dumps(build_alfa_order_bundle(order), ensure_ascii=False)
            tax_system = str(getattr(settings, "FISCAL_TAX_SYSTEM", "")).strip()
            if tax_system:
                payload["taxSystem"] = tax_system
        result = self._post("register", payload)
        bank_order_id = str(result.get("orderId", ""))
        form_url = str(result.get("formUrl", ""))
        if not bank_order_id or not form_url:
            raise PaymentProviderError("Alfa-Bank registration response has no orderId or formUrl.")
        return RegisteredPayment(bank_order_id=bank_order_id, form_url=form_url, raw=sanitize_provider_payload(result))

    def get_status(self, bank_order_id: str) -> ProviderPaymentStatus:
        result = self._post("getOrderStatusExtended", {"orderId": bank_order_id, "language": "ru"})
        payment_info = result.get("paymentAmountInfo") if isinstance(result.get("paymentAmountInfo"), dict) else {}

        def optional_int(value):
            try:
                return int(value) if value not in (None, "") else None
            except (TypeError, ValueError):
                return None

        return ProviderPaymentStatus(
            order_status=int(result.get("orderStatus", -1)),
            order_number=str(result.get("orderNumber", "")),
            amount_minor=optional_int(result.get("amount")),
            deposited_amount_minor=optional_int(payment_info.get("depositedAmount")),
            refunded_amount_minor=optional_int(payment_info.get("refundedAmount")),
            currency=str(result.get("currency", "")),
            raw=sanitize_provider_payload(result),
        )

    def refund(self, bank_order_id: str, amount_rub: int) -> dict[str, Any]:
        result = self._post("refund", {"orderId": bank_order_id, "amount": _minor_units(amount_rub)})
        return sanitize_provider_payload(result)
