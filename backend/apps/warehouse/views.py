from functools import wraps
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.catalog.models import Part, PartNumber, PriceOffer, Supplier
from apps.catalog.services import build_part_search_text, normalize_part_number, stable_slug
from apps.core.models import LegalDocument, LegalEntitySettings
from apps.leads.models import CustomerRequest
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.refunds.models import Refund
from . import cdek
from .forms import AdjustmentForm, ConfirmShipmentForm, OfferForm, PartForm, PurchaseForm, PurchaseLineFormSet, ReceiptForm, ShipmentForm, StockSettingsForm
from .models import Fulfillment, PurchaseLine, PurchaseOrder, Shipment, StockItem, StockMovement, WarehouseEvent
from .services import ORDER_STATUS_LABELS, adjust_stock, audit, process_order, receive_purchase, set_purchase_status


def warehouse_access(permission="warehouse.view_stockitem"):
    def decorator(view):
        @never_cache
        @staff_member_required
        @wraps(view)
        def guarded(request, *args, **kwargs):
            permissions = (permission,) if isinstance(permission, str) else permission
            if not request.user.has_perms(("warehouse.view_stockitem", *permissions)):
                raise PermissionDenied
            response = view(request, *args, **kwargs)
            response["X-Robots-Tag"] = "noindex, nofollow"
            response["Referrer-Policy"] = "same-origin"
            return response
        return guarded
    return decorator


def owner_access(view):
    """Allow the current owner and future members of the dormant owner role."""
    @never_cache
    @staff_member_required
    @wraps(view)
    def guarded(request, *args, **kwargs):
        is_owner = request.user.is_superuser or request.user.groups.filter(name="owner").exists()
        if not is_owner:
            raise PermissionDenied
        response = view(request, *args, **kwargs)
        response["X-Robots-Tag"] = "noindex, nofollow"
        response["Referrer-Policy"] = "same-origin"
        return response
    return guarded


REQUEST_STATUS_LABELS = {
    CustomerRequest.Status.NEW: "Новая",
    CustomerRequest.Status.IN_WORK: "В работе",
    CustomerRequest.Status.WAITING_CUSTOMER: "Ждём клиента",
    CustomerRequest.Status.DONE: "Завершена",
    CustomerRequest.Status.CANCELLED: "Отменена",
}
PAYMENT_STATUS_LABELS = {
    Payment.Status.DRAFT: "Черновик",
    Payment.Status.PENDING: "Ожидает оплаты",
    Payment.Status.SUCCEEDED: "Оплачен",
    Payment.Status.FAILED: "Ошибка",
    Payment.Status.CANCELLED: "Отменён",
    Payment.Status.PARTIALLY_REFUNDED: "Частично возвращён",
    Payment.Status.REFUNDED: "Возвращён",
}
REFUND_STATUS_LABELS = {
    Refund.Status.REQUESTED: "Запрошен",
    Refund.Status.APPROVED: "Одобрен",
    Refund.Status.PROCESSING: "Обрабатывается",
    Refund.Status.SUCCEEDED: "Выполнен",
    Refund.Status.FAILED: "Ошибка",
    Refund.Status.CANCELLED: "Отменён",
}


def add_status_labels(items, labels):
    for item in items:
        item.owner_status_label = labels.get(item.status, item.status)
    return items


@owner_access
@require_GET
def owner_dashboard(request):
    request_queue = list(
        CustomerRequest.objects.filter(
            status__in=[CustomerRequest.Status.NEW, CustomerRequest.Status.IN_WORK, CustomerRequest.Status.WAITING_CUSTOMER]
        ).prefetch_related("items")[:6]
    )
    order_queue = list(
        Order.objects.filter(
            status__in=[
                Order.Status.DRAFT,
                Order.Status.CONFIRMED_BY_MANAGER,
                Order.Status.PAYMENT_PENDING,
                Order.Status.PAID,
                Order.Status.FAILED,
            ]
        ).select_related("fulfillment")[:6]
    )
    payment_queue = list(
        Payment.objects.filter(status__in=[Payment.Status.DRAFT, Payment.Status.PENDING, Payment.Status.FAILED])
        .select_related("order")[:6]
    )
    refund_queue = list(
        Refund.objects.filter(status__in=[Refund.Status.REQUESTED, Refund.Status.APPROVED, Refund.Status.PROCESSING, Refund.Status.FAILED])
        .select_related("order", "payment")[:6]
    )
    add_status_labels(request_queue, REQUEST_STATUS_LABELS)
    add_status_labels(order_queue, ORDER_STATUS_LABELS)
    add_status_labels(payment_queue, PAYMENT_STATUS_LABELS)
    add_status_labels(refund_queue, REFUND_STATUS_LABELS)

    legal_entity = LegalEntitySettings.objects.first()
    required_legal_documents = len(LegalDocument.Kind.values)
    published_legal_documents = (
        LegalDocument.objects.filter(is_published=True).values("kind").distinct().count()
    )
    low_stock = StockItem.objects.filter(on_hand__lte=F("reserved") + F("minimum")).count()
    untracked_stock = Part.objects.filter(warehouse_stock__isnull=True).count()

    return render(request, "warehouse/owner_dashboard.html", {
        "section": "owner",
        "title": "Центр управления",
        "new_requests_count": CustomerRequest.objects.filter(status=CustomerRequest.Status.NEW).count(),
        "orders_to_confirm_count": Order.objects.filter(status=Order.Status.DRAFT).count(),
        "payments_attention_count": Payment.objects.filter(
            status__in=[Payment.Status.DRAFT, Payment.Status.PENDING, Payment.Status.FAILED]
        ).count(),
        "paid_to_fulfill_count": Order.objects.filter(status=Order.Status.PAID).filter(
            Q(fulfillment__isnull=True) | ~Q(fulfillment__status=Fulfillment.Status.DISPATCHED)
        ).count(),
        "low_stock_count": low_stock,
        "purchases_attention_count": PurchaseOrder.objects.filter(
            status__in=[PurchaseOrder.Status.ORDERED, PurchaseOrder.Status.PARTIAL]
        ).count(),
        "shipments_attention_count": Shipment.objects.filter(
            status__in=[Shipment.Status.SUBMITTING, Shipment.Status.ERROR]
        ).count(),
        "refunds_attention_count": Refund.objects.filter(
            status__in=[Refund.Status.REQUESTED, Refund.Status.APPROVED, Refund.Status.PROCESSING, Refund.Status.FAILED]
        ).count(),
        "request_queue": request_queue,
        "order_queue": order_queue,
        "payment_queue": payment_queue,
        "refund_queue": refund_queue,
        "legal_entity_ready": bool(legal_entity and legal_entity.is_ready_for_production),
        "published_legal_documents": published_legal_documents,
        "required_legal_documents": required_legal_documents,
        "untracked_stock_count": untracked_stock,
        "cdek_mode_label": cdek.mode_label(),
        "payments_enabled": settings.PAYMENTS_ENABLED,
        "payments_mode": settings.PAYMENTS_MODE,
        "fiscalization_enabled": settings.FISCALIZATION_ENABLED,
        "storefront_url": f"{settings.ZEMAZAP_SITE_URL.rstrip('/')}/",
    })


@warehouse_access()
@require_GET
def overview(request):
    return render(request, "warehouse/overview.html", {
        "section": "overview", "title": "Рабочий стол",
        "parts_count": Part.objects.count(),
        "suppliers_count": Supplier.objects.count(),
        "paid_count": Order.objects.filter(status=Order.Status.PAID).exclude(fulfillment__status=Fulfillment.Status.DISPATCHED).count(),
        "purchases_count": PurchaseOrder.objects.filter(status__in=["ordered", "partial"]).count(),
        "shipments_count": Shipment.objects.exclude(status__in=["draft", "cancelled", "delivered"]).count(),
        "cdek_mode_label": cdek.mode_label(),
        "recent_parts": Part.objects.select_related("brand", "manufacturer").order_by("-updated_at")[:6],
    })


def page_for(request, queryset):
    return Paginator(queryset, 25).get_page(request.GET.get("page"))


def feedback(request, callback, success):
    try:
        result = callback()
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
        return False
    messages.success(request, success if result is not False else "Операция уже выполнена. Повторных изменений нет.")
    return True


@warehouse_access("catalog.view_part")
@require_GET
def parts(request):
    queryset = Part.objects.select_related("brand", "manufacturer", "warehouse_stock").prefetch_related("price_offers")
    query, status = request.GET.get("q", "").strip()[:160], request.GET.get("status", "")
    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(primary_article__icontains=query) | Q(primary_oem__icontains=query))
    if status == "low":
        queryset = queryset.filter(warehouse_stock__on_hand__lte=F("warehouse_stock__reserved") + F("warehouse_stock__minimum"))
    elif status == "untracked":
        queryset = queryset.filter(warehouse_stock__isnull=True)
    elif status == "inactive":
        queryset = queryset.filter(is_active=False)
    return render(request, "warehouse/parts.html", {"section": "parts", "title": "Детали и остатки", "page": page_for(request, queryset), "q": query, "status": status})


@warehouse_access("catalog.view_part")
@require_http_methods(["GET", "POST"])
def part_detail(request, pk=None):
    part = get_object_or_404(Part.objects.select_related("brand", "manufacturer", "category"), pk=pk) if pk else Part()
    edit_perm = "catalog.change_part" if pk else "catalog.add_part"
    stock = StockItem.objects.filter(part_id=pk).first() if pk else None
    offer = part.price_offers.filter(is_primary=True).order_by("pk").first() if pk else None
    data = request.POST if request.method == "POST" else None
    form = PartForm(data, instance=part)
    stock_form = StockSettingsForm(data, instance=stock, prefix="stock")
    offer_form = OfferForm(data, prefix="offer", initial={"supplier": offer.supplier_id, "price_rub": offer.price_rub,
                            "availability": offer.availability, "delivery": offer.delivery} if offer else {"availability": Part.Availability.CHECK})
    if request.method == "POST":
        if not request.user.has_perms([edit_perm, "warehouse.manage_inventory"]):
            raise PermissionDenied
        valid = form.is_valid() & stock_form.is_valid() & offer_form.is_valid()
        if valid:
            with transaction.atomic():
                if pk:
                    Part.objects.select_for_update().get(pk=pk)
                part = form.save(commit=False)
                if not pk:
                    part.slug = stable_slug(part.name, max_length=120) + "-" + uuid.uuid4().hex[:8]
                part.search_text = build_part_search_text(name=part.name, article=part.primary_article, oem=part.primary_oem,
                    manufacturer=part.manufacturer.name, category=part.category.name, brand=part.brand.name, model=part.model_name,
                    condition=part.condition, quality=part.quality, analogs=list(part.numbers.filter(kind="analog").values_list("value", flat=True)) if pk else [],
                    compatibility=list(part.compatibility.values_list("label", flat=True)) if pk else [],
                    specs={s.name: s.value for s in part.specs.all()} if pk else {})
                part.save()
                for kind, value in [("article", part.primary_article), ("oem", part.primary_oem)]:
                    # Keep secondary identifiers; ensure the current primary remains searchable.
                    if value:
                        PartNumber.objects.get_or_create(part=part, kind=kind, value=value, defaults={"normalized_value": normalize_part_number(value)})
                current, _ = StockItem.objects.get_or_create(part=part)
                # Never write on_hand/reserved from a stale form instance.
                for name in ["location", "minimum", "unit_weight_g"]:
                    setattr(current, name, stock_form.cleaned_data[name])
                current.save(update_fields=["location", "minimum", "unit_weight_g", "updated_at"])
                if offer_form.cleaned_data["supplier"] is not None:
                    offer = offer or PriceOffer(part=part, is_primary=True)
                    for name in ["supplier", "price_rub", "availability", "delivery"]:
                        setattr(offer, name, offer_form.cleaned_data[name])
                    offer.save()
                audit(request.user, "Карточка детали сохранена", f"part:{part.pk}")
            messages.success(request, "Карточка сохранена. Физический остаток меняется только приёмкой или корректировкой.")
            return redirect("warehouse:part", pk=part.pk)
    return render(request, "warehouse/part.html", {"section": "parts", "title": part.name if pk else "Новая деталь", "part": part,
        "form": form, "stock_form": stock_form, "offer_form": offer_form, "stock": stock, "adjustment_form": AdjustmentForm(),
        "can_edit": request.user.has_perms([edit_perm, "warehouse.manage_inventory"]),
        "movements": StockMovement.objects.filter(stock__part_id=pk).select_related("actor")[:12] if pk else []})


@warehouse_access("warehouse.manage_inventory")
@require_POST
def part_adjust(request, pk):
    get_object_or_404(Part, pk=pk)
    form = AdjustmentForm(request.POST)
    if form.is_valid():
        feedback(request, lambda: adjust_stock(pk, form.cleaned_data["quantity"], form.cleaned_data["note"], request.user, form.cleaned_data["key"]), "Остаток скорректирован; операция записана в журнал.")
    else:
        messages.error(request, "Проверьте количество, причину и ключ операции. Обновите страницу и повторите ввод.")
    return redirect("warehouse:part", pk=pk)


@warehouse_access("warehouse.view_purchaseorder")
@require_GET
def purchases(request):
    queryset = PurchaseOrder.objects.select_related("supplier").prefetch_related("lines")
    q, status = request.GET.get("q", "").strip()[:160], request.GET.get("status", "")
    if q:
        queryset = queryset.filter(Q(supplier__name__icontains=q) | Q(reference__icontains=q) | Q(pk=int(q) if q.isdecimal() and len(q) < 12 else 0))
    if status in PurchaseOrder.Status.values:
        queryset = queryset.filter(status=status)
    return render(request, "warehouse/purchases.html", {"section": "purchases", "title": "Закупки", "page": page_for(request, queryset), "q": q,
        "status": status, "statuses": PurchaseOrder.Status.choices})


@warehouse_access("warehouse.process_purchases")
@require_http_methods(["GET", "POST"])
def purchase_create(request):
    purchase = PurchaseOrder(created_by=request.user)
    data = request.POST if request.method == "POST" else None
    form, formset = PurchaseForm(data, instance=purchase), PurchaseLineFormSet(data, instance=purchase)
    if request.method == "POST" and (form.is_valid() & formset.is_valid()):
        with transaction.atomic():
            purchase = form.save()
            formset.instance = purchase
            formset.save()
            audit(request.user, "Создана закупка", f"purchase:{purchase.pk}")
        return redirect("warehouse:purchase", pk=purchase.pk)
    return render(request, "warehouse/purchase_form.html", {"section": "purchases", "title": "Новая закупка", "form": form, "formset": formset})


@warehouse_access("warehouse.view_purchaseorder")
@require_GET
def purchase_detail(request, pk):
    purchase = get_object_or_404(PurchaseOrder.objects.select_related("supplier").prefetch_related("lines__part"), pk=pk)
    lines = []
    for line in purchase.lines.all():
        line.receipt_form = ReceiptForm(initial={"line_id": line.pk, "quantity": line.remaining})
        lines.append(line)
    return render(request, "warehouse/purchase.html", {"section": "purchases", "title": f"Закупка № {pk}", "purchase": purchase, "lines": lines})


@warehouse_access("warehouse.process_purchases")
@require_POST
def purchase_action(request, pk):
    get_object_or_404(PurchaseOrder, pk=pk)
    if request.POST.get("action") == "receive":
        form = ReceiptForm(request.POST)
        if form.is_valid():
            get_object_or_404(PurchaseLine, pk=form.cleaned_data["line_id"], purchase_id=pk)
            feedback(request, lambda: receive_purchase(pk, form.cleaned_data["line_id"], form.cleaned_data["quantity"], request.user, form.cleaned_data["key"]), "Приёмка записана. Остаток увеличен на принятое количество.")
        else:
            messages.error(request, "Проверьте количество приёмки. Обновите страницу перед повтором.")
    else:
        feedback(request, lambda: set_purchase_status(pk, request.POST.get("action"), request.user), "Статус закупки обновлён.")
    return redirect("warehouse:purchase", pk=pk)


ORDER_ACCESS = ("orders.view_order", "orders.view_order_pii")


@warehouse_access(ORDER_ACCESS)
@require_GET
def orders(request):
    queryset = Order.objects.select_related("fulfillment", "shipment")
    q, status = request.GET.get("q", "").strip()[:160], request.GET.get("status", "")
    if q:
        queryset = queryset.filter(Q(customer_name__icontains=q) | Q(items__article__icontains=q) | Q(pk=int(q) if q.isdecimal() and len(q) < 12 else 0)).distinct()
    if status == "unprocessed":
        queryset = queryset.filter(status="paid").filter(Q(fulfillment__isnull=True) | Q(fulfillment__status="new"))
    elif status in Fulfillment.Status.values:
        queryset = queryset.filter(fulfillment__status=status)
    page = page_for(request, queryset)
    for order in page:
        order.status_label = ORDER_STATUS_LABELS.get(order.status, order.status)
    return render(request, "warehouse/orders.html", {"section": "orders", "title": "Заказы покупателей", "page": page, "q": q, "status": status,
        "statuses": [("unprocessed", "Оплачены, не в сборке"), *Fulfillment.Status.choices]})


@warehouse_access(ORDER_ACCESS)
@require_GET
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related("fulfillment", "shipment").prefetch_related("items__part__warehouse_stock"), pk=pk)
    order.status_label = ORDER_STATUS_LABELS.get(order.status, order.status)
    return render(request, "warehouse/order.html", {"section": "orders", "title": f"Заказ № {pk}", "order": order,
        "fulfillment": getattr(order, "fulfillment", None), "shipment": getattr(order, "shipment", None)})


@warehouse_access((*ORDER_ACCESS, "warehouse.process_fulfillment"))
@require_POST
def order_action(request, pk):
    get_object_or_404(Order, pk=pk)
    action = request.POST.get("action")
    if action == "dispatch" and request.POST.get("confirm") != "on":
        messages.error(request, "Подтвердите фактическую передачу посылки перевозчику.")
    else:
        feedback(request, lambda: process_order(pk, action, request.user), "Складской статус заказа обновлён.")
    return redirect("warehouse:order", pk=pk)


@warehouse_access((*ORDER_ACCESS, "warehouse.view_shipment"))
@require_GET
def shipments(request):
    queryset = Shipment.objects.select_related("order")
    q, status = request.GET.get("q", "").strip()[:160], request.GET.get("status", "")
    if q:
        queryset = queryset.filter(Q(cdek_number__icontains=q) | Q(city_label__icontains=q) | Q(order_id=int(q) if q.isdecimal() and len(q) < 12 else 0))
    if status in Shipment.Status.values:
        queryset = queryset.filter(status=status)
    return render(request, "warehouse/shipments.html", {"section": "shipments", "title": "Доставка СДЭК", "page": page_for(request, queryset), "q": q, "status": status,
        "statuses": Shipment.Status.choices, "cdek_mode_label": cdek.mode_label()})


@warehouse_access((*ORDER_ACCESS, "warehouse.manage_shipments"))
@require_http_methods(["GET", "POST"])
def shipment_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    shipment = Shipment.objects.filter(order=order).first()
    editable = not shipment or shipment.status == Shipment.Status.DRAFT
    data = request.POST if request.method == "POST" else None
    form = ShipmentForm(data, instance=shipment, initial={"recipient_name": order.customer_name, "recipient_phone": order.contact} if not shipment else None)
    if request.method == "POST":
        if not editable:
            messages.error(request, "Зарегистрированную заявку нельзя менять здесь. Изменения согласуются в кабинете СДЭК.")
        elif form.is_valid():
            with transaction.atomic():
                Order.objects.select_for_update().get(pk=order_id)
                current = Shipment.objects.select_for_update().filter(order=order).first()
                if current and (not shipment or current.status != Shipment.Status.DRAFT):
                    messages.error(request, "Другой менеджер изменил отправление. Обновите страницу.")
                    return redirect("warehouse:shipment", order_id=order_id)
                shipment = form.save(commit=False)
                shipment.order = order
                shipment.quoted_price, shipment.quoted_at, shipment.quote_days = None, None, ""
                shipment.save()
                audit(request.user, "Черновик СДЭК сохранён", f"shipment:{shipment.pk}")
            messages.success(request, "Черновик сохранён. Данные ещё не отправлены в СДЭК.")
            return redirect("warehouse:shipment", order_id=order_id)
    return render(request, "warehouse/shipment.html", {"section": "shipments", "title": f"СДЭК · заказ № {order_id}", "order": order,
        "shipment": shipment, "form": form, "editable": editable, "confirm_form": ConfirmShipmentForm(), "cdek_mode_label": cdek.mode_label()})


@warehouse_access((*ORDER_ACCESS, "warehouse.manage_shipments"))
@require_POST
def shipment_action(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    action = request.POST.get("action")
    if action == "submit":
        if ConfirmShipmentForm(request.POST).is_valid():
            feedback(request, lambda: cdek.submit_shipment(pk, request.user), "Заявка передана в СДЭК. Обновите статус, чтобы проверить регистрацию.")
        else:
            messages.error(request, "Подтвердите отправку данных в СДЭК.")
    elif action == "quote":
        feedback(request, lambda: cdek.quote_shipment(shipment, request.user), "Расчёт обновлён. Это оценка, не окончательный счёт перевозчика.")
    elif action == "sync":
        feedback(request, lambda: cdek.sync_shipment(pk, request.user), "Статус отправления обновлён.")
    elif action == "label":
        feedback(request, lambda: cdek.prepare_label(shipment, request.user), "Печатная форма запрошена. Нажмите «Скачать PDF», когда она будет готова.")
    else:
        messages.error(request, "Неизвестное действие.")
    return redirect("warehouse:shipment", order_id=shipment.order_id)


@warehouse_access((*ORDER_ACCESS, "warehouse.manage_shipments"))
@require_GET
def shipment_label(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    try:
        pdf = cdek.download_label(shipment)
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
        return redirect("warehouse:shipment", order_id=shipment.order_id)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="cdek-order-{shipment.order_id}.pdf"'
    return response


@warehouse_access("warehouse.view_stockmovement")
@require_GET
def activity(request):
    queryset = StockMovement.objects.select_related("stock__part", "actor")
    kind = request.GET.get("kind", "")
    if kind in StockMovement.Kind.values:
        queryset = queryset.filter(kind=kind)
    return render(request, "warehouse/activity.html", {"section": "activity", "title": "Журнал операций", "page": page_for(request, queryset),
        "kind": kind, "kinds": StockMovement.Kind.choices, "events": WarehouseEvent.objects.select_related("actor")[:20]})
