import uuid

from django.conf import settings
from django.db import models
from django.db.models import F, Q


class StockItem(models.Model):
    part = models.OneToOneField("catalog.Part", on_delete=models.PROTECT, related_name="warehouse_stock")
    location = models.CharField("Ячейка хранения", max_length=80, blank=True)
    on_hand = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    minimum = models.PositiveIntegerField("Минимальный остаток", default=0)
    unit_weight_g = models.PositiveIntegerField("Вес одной детали, г", default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("manage_inventory", "Can adjust physical warehouse inventory"),
            ("process_purchases", "Can place and receive purchase orders"),
            ("process_fulfillment", "Can reserve, pack and dispatch customer orders"),
            ("manage_shipments", "Can prepare and submit CDEK shipments"),
        ]
        constraints = [models.CheckConstraint(condition=Q(reserved__lte=F("on_hand")), name="warehouse_reserved_within_stock")]

    @property
    def available(self):
        return self.on_hand - self.reserved

    def __str__(self):
        return f"{self.part} · {self.on_hand} шт."


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        ORDERED = "ordered", "Ожидаем поставку"
        PARTIAL = "partial", "Принято частично"
        RECEIVED = "received", "Принято полностью"
        CANCELLED = "cancelled", "Отменена"

    supplier = models.ForeignKey("catalog.Supplier", on_delete=models.PROTECT)
    reference = models.CharField("Номер у поставщика", max_length=100, blank=True)
    expected_at = models.DateField("Ожидаемая дата", null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    note = models.TextField("Примечание", blank=True, max_length=2000)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total(self):
        return sum(line.quantity * line.unit_cost_rub for line in self.lines.all())

    def __str__(self):
        return f"Закупка #{self.pk} · {self.supplier}"


class PurchaseLine(models.Model):
    purchase = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    part = models.ForeignKey("catalog.Part", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField("Заказано", default=1)
    received = models.PositiveIntegerField(default=0)
    unit_cost_rub = models.DecimalField("Цена закупки, ₽", max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gt=0), name="warehouse_purchase_positive_qty"),
            models.CheckConstraint(condition=Q(received__lte=F("quantity")), name="warehouse_receipt_within_order"),
            models.CheckConstraint(condition=Q(unit_cost_rub__gte=0), name="warehouse_purchase_nonnegative_cost"),
            models.UniqueConstraint(fields=["purchase", "part"], name="warehouse_unique_purchase_part"),
        ]

    @property
    def remaining(self):
        return self.quantity - self.received


class Fulfillment(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Не в сборке"
        RESERVED = "reserved", "В сборке"
        PACKED = "packed", "Упакован"
        DISPATCHED = "dispatched", "Передан в доставку"

    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="fulfillment")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


class Reservation(models.Model):
    fulfillment = models.ForeignKey(Fulfillment, on_delete=models.CASCADE, related_name="reservations")
    stock = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["fulfillment", "stock"], name="warehouse_unique_reservation"),
            models.CheckConstraint(condition=Q(quantity__gt=0), name="warehouse_reservation_positive_qty"),
        ]


class Shipment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SUBMITTING = "submitting", "Проверить регистрацию"
        ACCEPTED = "accepted", "Регистрация обрабатывается"
        READY = "ready", "Зарегистрирован в СДЭК"
        TRANSIT = "transit", "В пути"
        DELIVERED = "delivered", "Доставлен"
        CANCELLED = "cancelled", "Отменён в СДЭК"
        ERROR = "error", "Требует внимания"

    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="shipment")
    client_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    mode = models.CharField(max_length=10, blank=True)
    tariff_code = models.PositiveIntegerField("Код тарифа СДЭК", default=136)
    recipient_name = models.CharField("ФИО получателя", max_length=160)
    recipient_phone = models.CharField("Телефон получателя", max_length=30)
    city_code = models.PositiveIntegerField("Код города СДЭК")
    city_label = models.CharField("Город (для менеджера)", max_length=160)
    delivery_point = models.CharField("Код ПВЗ СДЭК", max_length=30, blank=True)
    address = models.CharField("Адрес для доставки до двери", max_length=240, blank=True)
    weight_g = models.PositiveIntegerField("Вес посылки с упаковкой, г")
    length_cm = models.PositiveIntegerField("Длина, см")
    width_cm = models.PositiveIntegerField("Ширина, см")
    height_cm = models.PositiveIntegerField("Высота, см")
    cdek_uuid = models.UUIDField(null=True, blank=True, unique=True)
    cdek_number = models.CharField(max_length=40, blank=True)
    provider_status = models.CharField(max_length=80, blank=True)
    last_error = models.CharField(max_length=240, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    quoted_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quote_days = models.CharField(max_length=60, blank=True)
    quoted_at = models.DateTimeField(null=True, blank=True)
    label_uuid = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"СДЭК · заказ #{self.order_id}"


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        ADJUSTMENT = "adjustment", "Корректировка"
        RECEIPT = "receipt", "Приёмка"
        RESERVE = "reserve", "Резерв"
        RELEASE = "release", "Снятие резерва"
        DISPATCH = "dispatch", "Отгрузка"

    stock = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name="movements")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    quantity = models.IntegerField(default=0)
    reserved_delta = models.IntegerField(default=0)
    balance_after = models.PositiveIntegerField()
    reserved_after = models.PositiveIntegerField()
    note = models.CharField(max_length=500, blank=True)
    purchase = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, null=True, blank=True)
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, null=True, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    idempotency_key = models.UUIDField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]


class WarehouseEvent(models.Model):
    """Minimal audit: action and record IDs, never carrier payloads or customer PII."""
    action = models.CharField(max_length=160)
    target = models.CharField(max_length=100)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
