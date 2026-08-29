from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalog.models import Part
from apps.orders.models import Order

from .models import Fulfillment, PurchaseLine, PurchaseOrder, Reservation, Shipment, StockItem, StockMovement, WarehouseEvent


def audit(actor, action, target):
    WarehouseEvent.objects.create(actor=actor, action=action, target=target)


def locked_stock(part_id):
    # Lock the parent even when there is no StockItem yet, serializing first receipts.
    Part.objects.select_for_update().get(pk=part_id)
    stock, _ = StockItem.objects.get_or_create(part_id=part_id)
    return StockItem.objects.select_for_update().get(pk=stock.pk)


def movement(stock, kind, actor, *, quantity=0, reserved_delta=0, note="", order=None, purchase=None, key=None):
    stock.on_hand += quantity
    stock.reserved += reserved_delta
    if stock.on_hand < 0 or stock.reserved < 0 or stock.reserved > stock.on_hand:
        raise ValidationError("Недостаточно свободного остатка. Проверьте резервы и количество.")
    stock.save(update_fields=["on_hand", "reserved", "updated_at"])
    return StockMovement.objects.create(
        stock=stock, kind=kind, actor=actor, quantity=quantity, reserved_delta=reserved_delta,
        balance_after=stock.on_hand, reserved_after=stock.reserved, note=note,
        order=order, purchase=purchase, idempotency_key=key,
    )


@transaction.atomic
def adjust_stock(part_id, quantity, note, actor, key):
    if not note.strip() or not quantity or not key:
        raise ValidationError("Укажите ненулевое изменение остатка и причину.")
    stock = locked_stock(part_id)
    if StockMovement.objects.filter(idempotency_key=key).exists():
        return False
    movement(stock, StockMovement.Kind.ADJUSTMENT, actor, quantity=quantity, note=note, key=key)
    return True


@transaction.atomic
def set_purchase_status(purchase_id, action, actor):
    purchase = PurchaseOrder.objects.select_for_update().get(pk=purchase_id)
    if action == "order" and purchase.status == PurchaseOrder.Status.DRAFT:
        if not purchase.lines.exists():
            raise ValidationError("В закупке нет позиций.")
        purchase.status = PurchaseOrder.Status.ORDERED
    elif action == "cancel" and purchase.status in {PurchaseOrder.Status.DRAFT, PurchaseOrder.Status.ORDERED}:
        purchase.status = PurchaseOrder.Status.CANCELLED
    else:
        raise ValidationError("Этот переход недоступен. Обновите страницу закупки.")
    purchase.save(update_fields=["status", "updated_at"])
    audit(actor, f"Закупка: {purchase.get_status_display()}", f"purchase:{purchase.pk}")


@transaction.atomic
def receive_purchase(purchase_id, line_id, quantity, actor, key):
    purchase = PurchaseOrder.objects.select_for_update().get(pk=purchase_id)
    if StockMovement.objects.filter(idempotency_key=key).exists():
        return False
    if purchase.status not in {PurchaseOrder.Status.ORDERED, PurchaseOrder.Status.PARTIAL}:
        raise ValidationError("Приёмка доступна только для ожидаемой или частичной поставки.")
    line = PurchaseLine.objects.select_for_update().get(pk=line_id, purchase=purchase)
    if not key or quantity <= 0 or quantity > line.remaining:
        raise ValidationError("Количество должно быть больше нуля и не превышать ожидаемое.")
    stock = locked_stock(line.part_id)
    movement(stock, StockMovement.Kind.RECEIPT, actor, quantity=quantity, purchase=purchase, key=key)
    line.received += quantity
    line.save(update_fields=["received"])
    purchase.status = (PurchaseOrder.Status.RECEIVED if all(row.remaining == 0 for row in purchase.lines.all()) else PurchaseOrder.Status.PARTIAL)
    purchase.save(update_fields=["status", "updated_at"])
    return True


def order_quantities(order):
    quantities = defaultdict(int)
    items = list(order.items.select_related("part"))
    if not items:
        raise ValidationError("В заказе нет деталей.")
    for item in items:
        if not item.part_id or item.quantity <= 0:
            raise ValidationError("Каждая позиция должна быть связана с деталью каталога и иметь положительное количество.")
        if not item.part.is_active or item.part.sale_blocked_by_marking:
            raise ValidationError(f"Деталь «{item.part.name}» скрыта или заблокирована маркировкой.")
        quantities[item.part_id] += item.quantity
    return dict(quantities)


def check_reserved_items(order, fulfillment):
    reserved = {row.stock.part_id: row.quantity for row in fulfillment.reservations.select_related("stock")}
    if reserved != order_quantities(order):
        raise ValidationError("Состав заказа изменён после резерва. Снимите резерв и соберите заказ заново.")


@transaction.atomic
def process_order(order_id, action, actor):
    order = Order.objects.select_for_update().get(pk=order_id)
    fulfillment, _ = Fulfillment.objects.get_or_create(order=order)
    fulfillment = Fulfillment.objects.select_for_update().get(pk=fulfillment.pk)
    shipment = Shipment.objects.filter(order=order).first()
    if action == "reserve":
        if fulfillment.status != Fulfillment.Status.NEW:
            raise ValidationError("Заказ уже в сборке или отгружен.")
        if order.status not in {Order.Status.CONFIRMED_BY_MANAGER, Order.Status.PAYMENT_PENDING, Order.Status.PAID}:
            raise ValidationError("Сначала менеджер должен подтвердить заказ.")
        quantities = order_quantities(order)
        for part_id, quantity in sorted(quantities.items()):
            stock = locked_stock(part_id)
            if quantity > stock.available:
                raise ValidationError(f"Недостаточно остатка: {stock.part.name}. Доступно {stock.available}, нужно {quantity}.")
            movement(stock, StockMovement.Kind.RESERVE, actor, reserved_delta=quantity, order=order)
            Reservation.objects.create(fulfillment=fulfillment, stock=stock, quantity=quantity)
        fulfillment.status = Fulfillment.Status.RESERVED
    elif action == "release":
        if fulfillment.status not in {Fulfillment.Status.RESERVED, Fulfillment.Status.PACKED}:
            raise ValidationError("У заказа нет действующего резерва.")
        if shipment and shipment.status not in {Shipment.Status.DRAFT, Shipment.Status.CANCELLED}:
            raise ValidationError("Сначала отмените отправление в СДЭК и обновите его статус.")
        for row in fulfillment.reservations.select_related("stock").order_by("stock__part_id"):
            stock = locked_stock(row.stock.part_id)
            movement(stock, StockMovement.Kind.RELEASE, actor, reserved_delta=-row.quantity, order=order)
        fulfillment.reservations.all().delete()
        fulfillment.status = Fulfillment.Status.NEW
    elif action == "pack":
        if fulfillment.status != Fulfillment.Status.RESERVED or order.status != Order.Status.PAID:
            raise ValidationError("Упаковка доступна после резерва и подтверждённой оплаты.")
        check_reserved_items(order, fulfillment)
        fulfillment.status = Fulfillment.Status.PACKED
    elif action == "dispatch":
        if fulfillment.status != Fulfillment.Status.PACKED or order.status != Order.Status.PAID:
            raise ValidationError("Отгрузить можно только оплаченный и упакованный заказ.")
        check_reserved_items(order, fulfillment)
        if not shipment or not shipment.cdek_number or shipment.mode != "prod" or shipment.status not in {Shipment.Status.READY, Shipment.Status.TRANSIT, Shipment.Status.DELIVERED}:
            raise ValidationError("Для отгрузки требуется зарегистрированная production-накладная СДЭК.")
        for row in fulfillment.reservations.select_related("stock").order_by("stock__part_id"):
            stock = locked_stock(row.stock.part_id)
            movement(stock, StockMovement.Kind.DISPATCH, actor, quantity=-row.quantity, reserved_delta=-row.quantity, order=order)
        fulfillment.reservations.all().delete()
        fulfillment.status = Fulfillment.Status.DISPATCHED
    else:
        raise ValidationError("Неизвестное действие.")
    fulfillment.save(update_fields=["status", "updated_at"])
    audit(actor, f"Сборка: {fulfillment.get_status_display()}", f"order:{order.pk}")


ORDER_STATUS_LABELS = {
    "draft": "Черновик", "confirmed_by_manager": "Подтверждён", "payment_pending": "Ожидает оплаты",
    "paid": "Оплачен", "failed": "Ошибка оплаты", "cancelled": "Отменён", "fulfilled": "Выполнен",
    "refunded": "Возврат", "partially_refunded": "Частичный возврат",
}
