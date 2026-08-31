"""CDEK API v2. No live calls unless explicitly enabled; no carrier payloads in logs."""
import json
import re
import uuid
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.orders.models import Order
from .models import Fulfillment, Shipment, StockItem
from .services import audit, check_reserved_items


class CdekError(ValidationError):
    pass


TRANSIT_CODES = {
    "RECEIVED_AT_SHIPMENT_WAREHOUSE", "READY_FOR_SHIPMENT_IN_SENDER_CITY",
    "TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY", "SENT_TO_TRANSIT_CITY",
    "ACCEPTED_IN_TRANSIT_CITY", "ACCEPTED_AT_TRANSIT_WAREHOUSE",
    "READY_FOR_SHIPMENT_IN_TRANSIT_CITY", "TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY",
    "SENT_TO_RECIPIENT_CITY", "ACCEPTED_IN_RECIPIENT_CITY",
    "ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE", "ACCEPTED_AT_PICK_UP_POINT", "TAKEN_BY_COURIER",
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def mode_label():
    if not settings.CDEK_ENABLED:
        return "API выключен"
    return "Тестовый контур" if settings.CDEK_MODE == "test" else "Рабочий контур"


class CdekClient:
    def __init__(self, mode=None):
        mode = mode or settings.CDEK_MODE
        if not settings.CDEK_ENABLED or mode not in {"test", "prod"}:
            raise CdekError("API СДЭК выключен или его режим не настроен.")
        if mode != settings.CDEK_MODE:
            raise CdekError("Режим этой накладной отличается от текущего подключения СДЭК.")
        if not settings.CDEK_CLIENT_ID or not settings.CDEK_CLIENT_SECRET:
            raise CdekError("Не заданы учётные данные API СДЭК.")
        self.base = "https://api.edu.cdek.ru/v2" if mode == "test" else "https://api.cdek.ru/v2"
        self.token = None

    def _request(self, method, path, data=None, *, form=False, pdf=False):
        headers = {"Accept": "application/pdf" if pdf else "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        body = None
        if data is not None:
            body = urlencode(data).encode() if form else json.dumps(data, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
        request = Request(self.base + path, data=body, headers=headers, method=method)
        try:
            with build_opener(NoRedirect()).open(request, timeout=max(3, min(settings.CDEK_TIMEOUT_SECONDS, 30))) as response:
                limit = 10 * 1024 * 1024 if pdf else 2 * 1024 * 1024
                raw = response.read(limit + 1)
                if len(raw) > limit:
                    raise CdekError("Ответ СДЭК превышает допустимый размер.")
        except HTTPError as exc:
            raise CdekError(f"СДЭК вернул HTTP {exc.code}. Проверьте подключение или статус отправления.") from None
        except (URLError, TimeoutError, OSError):
            raise CdekError("Нет подтверждённого ответа СДЭК. Обновите статус; не создавайте дубликат отправления.") from None
        if pdf:
            if not raw.startswith(b"%PDF-"):
                raise CdekError("Печатная форма ещё не готова. Повторите скачивание позже.")
            return raw
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            raise CdekError("Не удалось прочитать ответ СДЭК. Проверьте статус отправления.") from None
        return payload

    def request(self, method, path, data=None, *, pdf=False):
        if not self.token:
            auth = self._request("POST", "/oauth/token", {
                "grant_type": "client_credentials", "client_id": settings.CDEK_CLIENT_ID,
                "client_secret": settings.CDEK_CLIENT_SECRET,
            }, form=True)
            self.token = auth.get("access_token")
            if not self.token:
                raise CdekError("СДЭК не подтвердил авторизацию.")
        return self._request(method, path, data, pdf=pdf)


def raise_provider_errors(payload):
    errors = list(payload.get("errors") or [])
    for request in payload.get("requests") or []:
        errors.extend(request.get("errors") or [])
        if request.get("state") in {"INVALID", "FAILED"} and not errors:
            errors.append({"code": request["state"]})
    if errors:
        # Error messages may echo recipient PII; expose only bounded identifier codes.
        codes = [re.sub(r"[^A-Za-z0-9_.-]", "", str(e.get("code", "error")))[:60] for e in errors[:3]]
        raise CdekError("СДЭК отклонил запрос: " + ", ".join(codes) + ". Проверьте данные в кабинете СДЭК.")


def package_data(shipment):
    return {"weight": shipment.weight_g, "length": shipment.length_cm, "width": shipment.width_cm, "height": shipment.height_cm}


def from_location():
    if settings.CDEK_SENDER_CITY_CODE <= 0 or not settings.CDEK_SENDER_ADDRESS:
        raise CdekError("Не заполнены код города и адрес отправителя СДЭК.")
    return {"code": settings.CDEK_SENDER_CITY_CODE, "address": settings.CDEK_SENDER_ADDRESS}


def shipment_payload(shipment):
    order = shipment.order
    fulfillment = getattr(order, "fulfillment", None)
    if order.status != Order.Status.PAID or not fulfillment or fulfillment.status != Fulfillment.Status.PACKED:
        raise CdekError("Отправление создаётся только для оплаченного и упакованного заказа.")
    check_reserved_items(order, fulfillment)
    if not settings.CDEK_SENDER_NAME or not settings.CDEK_SENDER_PHONE:
        raise CdekError("Не заполнены имя и телефон отправителя СДЭК.")
    items, total_weight = [], 0
    for item in order.items.select_related("part"):
        stock = StockItem.objects.get(part=item.part)
        if stock.unit_weight_g <= 0:
            raise CdekError(f"Укажите вес детали «{item.part_name}» в её карточке.")
        total_weight += stock.unit_weight_g * item.quantity
        items.append({"name": item.part_name[:255], "ware_key": item.article or str(item.part_id),
                      "payment": {"value": 0}, "cost": item.unit_price_rub, "weight": stock.unit_weight_g, "amount": item.quantity})
    if shipment.weight_g < total_weight:
        raise CdekError("Вес посылки меньше суммарного веса деталей.")
    payload = {"type": 1, "number": str(shipment.client_number), "tariff_code": shipment.tariff_code,
               "sender": {"name": settings.CDEK_SENDER_NAME, "phones": [{"number": settings.CDEK_SENDER_PHONE}]},
               "recipient": {"name": shipment.recipient_name, "phones": [{"number": shipment.recipient_phone}]},
               "from_location": from_location(), "packages": [{"number": "1", **package_data(shipment), "items": items}]}
    if shipment.delivery_point:
        payload["delivery_point"] = shipment.delivery_point
    else:
        payload["to_location"] = {"code": shipment.city_code, "address": shipment.address}
    return payload


def quote_shipment(shipment, actor):
    if shipment.status != Shipment.Status.DRAFT:
        raise CdekError("Расчёт доступен только для черновика.")
    payload = {"type": 1, "tariff_code": shipment.tariff_code, "currency": 1,
               "from_location": from_location(), "to_location": {"code": shipment.city_code},
               "packages": [package_data(shipment)]}
    if shipment.delivery_point:
        payload["delivery_point"] = shipment.delivery_point
    result = CdekClient().request("POST", "/calculator/tariff", payload)
    raise_provider_errors(result)
    try:
        price = Decimal(str(result["total_sum"]))
        if not price.is_finite() or price < 0 or price >= 10000000000:
            raise ValueError
        period_min, period_max = int(result["period_min"]), int(result["period_max"])
    except (KeyError, TypeError, ValueError, InvalidOperation):
        raise CdekError("СДЭК не вернул корректную стоимость и срок доставки.") from None
    # Do not overwrite a quote if another manager edited the draft while HTTP was in flight.
    changed = Shipment.objects.filter(pk=shipment.pk, updated_at=shipment.updated_at).update(
        quoted_price=price, quote_days=f"{period_min}–{period_max} рабочих дней", quoted_at=timezone.now())
    if not changed:
        raise CdekError("Черновик изменён. Повторите расчёт для новых данных.")
    audit(actor, "Расчёт тарифа СДЭК", f"shipment:{shipment.pk}")


def submit_shipment(shipment_id, actor):
    # Commit SUBMITTING before HTTP. A timeout/crash leaves reconciliation-only state.
    order_id = Shipment.objects.values_list("order_id", flat=True).get(pk=shipment_id)
    client = CdekClient()
    with transaction.atomic():
        Order.objects.select_for_update().get(pk=order_id)
        shipment = Shipment.objects.select_for_update().select_related("order").get(pk=shipment_id)
        if shipment.status != Shipment.Status.DRAFT or shipment.cdek_uuid:
            raise CdekError("Отправление уже подавалось. Используйте обновление статуса, не повторную отправку.")
        payload = shipment_payload(shipment)
        shipment.status, shipment.mode, shipment.last_error = Shipment.Status.SUBMITTING, settings.CDEK_MODE, ""
        shipment.save(update_fields=["status", "mode", "last_error", "updated_at"])
        audit(actor, "Отправка заявки в СДЭК", f"shipment:{shipment.pk}")
    try:
        result = client.request("POST", "/orders", payload)
        entity = result.get("entity") or {}
        if entity.get("uuid"):
            Shipment.objects.filter(pk=shipment_id).update(cdek_uuid=uuid.UUID(entity["uuid"]))
        raise_provider_errors(result)
        if not entity.get("uuid"):
            raise CdekError("СДЭК не вернул идентификатор. Используйте обновление статуса.")
        Shipment.objects.filter(pk=shipment_id).update(status=Shipment.Status.ACCEPTED, last_error="", updated_at=timezone.now())
    except (ValidationError, ValueError, TypeError) as exc:
        message = "; ".join(exc.messages) if isinstance(exc, ValidationError) else "Некорректный идентификатор в ответе СДЭК. Обновите статус."
        Shipment.objects.filter(pk=shipment_id).update(last_error=message[:240])
        raise CdekError(message) from None


def sync_shipment(shipment_id, actor=None):
    shipment = Shipment.objects.get(pk=shipment_id)
    if shipment.status == Shipment.Status.DRAFT:
        raise CdekError("Черновик ещё не отправлен в СДЭК.")
    path = f"/orders/{shipment.cdek_uuid}" if shipment.cdek_uuid else "/orders?" + urlencode({"im_number": str(shipment.client_number)})
    result = CdekClient(shipment.mode).request("GET", path)
    entity = result.get("entity") or {}
    # Historical UPDATE errors must not hide a valid current order.
    if not entity.get("uuid"):
        raise_provider_errors(result)
    try:
        carrier_uuid = uuid.UUID(entity["uuid"])
        if entity.get("number") != str(shipment.client_number):
            raise ValueError
    except (KeyError, ValueError, TypeError):
        raise CdekError("Не найдено однозначное подтверждение этой заявки. Проверьте её номер в кабинете СДЭК.") from None
    if shipment.cdek_uuid and carrier_uuid != shipment.cdek_uuid:
        raise CdekError("СДЭК вернул другой идентификатор отправления.")
    statuses = [item for item in entity.get("statuses") or [] if not item.get("deleted")]
    def status_time(item):
        try:
            value = parse_datetime(str(item.get("date_time", "")))
        except ValueError:
            return 0
        return value.timestamp() if value else 0
    latest = max(statuses, key=status_time, default={})
    code = re.sub(r"[^A-Z0-9_]", "", str(latest.get("code", "")))[:80]
    state = Shipment.Status.READY if entity.get("cdek_number") else Shipment.Status.ACCEPTED
    error = ""
    if code == "DELIVERED":
        state = Shipment.Status.DELIVERED
    elif code == "REMOVED":
        state = Shipment.Status.CANCELLED
    elif code in TRANSIT_CODES:
        state = Shipment.Status.TRANSIT
    elif code and code != "CREATED":
        state, error = Shipment.Status.ERROR, "Проверьте статус в СДЭК. Автоматической приёмки возвратов нет."
    if entity.get("is_return") or entity.get("is_client_return"):
        state, error = Shipment.Status.ERROR, "Возврат перевозчика: проверьте поступление товара вручную."
    changed = Shipment.objects.filter(pk=shipment_id, updated_at=shipment.updated_at).update(
        cdek_uuid=carrier_uuid, cdek_number=str(entity.get("cdek_number") or "")[:40],
        provider_status=code, status=state, last_error=error, last_synced_at=timezone.now(), updated_at=timezone.now())
    if not changed:
        raise CdekError("Отправление изменилось во время проверки. Повторите обновление статуса.")
    audit(actor, "Статус СДЭК обновлён", f"shipment:{shipment_id}")


def prepare_label(shipment, actor):
    if not shipment.cdek_uuid or not shipment.cdek_number or shipment.status in {Shipment.Status.CANCELLED, Shipment.Status.ERROR}:
        raise CdekError("Сначала дождитесь регистрации отправления в СДЭК.")
    if shipment.label_uuid:
        return
    result = CdekClient(shipment.mode).request("POST", "/print/orders", {"orders": [{"order_uuid": str(shipment.cdek_uuid)}], "copy_count": 1})
    raise_provider_errors(result)
    try:
        label_uuid = uuid.UUID(result["entity"]["uuid"])
    except (KeyError, ValueError, TypeError):
        raise CdekError("СДЭК не вернул идентификатор печатной формы.") from None
    Shipment.objects.filter(pk=shipment.pk).update(label_uuid=label_uuid)
    audit(actor, "Печатная форма СДЭК запрошена", f"shipment:{shipment.pk}")


def download_label(shipment):
    if not shipment.label_uuid:
        raise CdekError("Сначала запросите печатную форму.")
    # Fixed CDEK endpoint, never a provider-supplied download URL (SSRF/redirect protection).
    return CdekClient(shipment.mode).request("GET", f"/print/orders/{shipment.label_uuid}.pdf", pdf=True)
