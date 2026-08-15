from __future__ import annotations

from django.conf import settings
from django.db import transaction

from apps.leads.models import CustomerRequest

from .models import Order, OrderItem, OrderStatusHistory


@transaction.atomic
def create_order_from_request(customer_request: CustomerRequest, note: str = "") -> tuple[Order, bool]:
    existing_order = getattr(customer_request, "order", None)
    if existing_order:
        return existing_order, False

    order = Order.objects.create(
        request=customer_request,
        customer_name=customer_request.customer_name,
        contact=customer_request.contact,
        vehicle=customer_request.vehicle,
        manager_note=note,
        total_amount_rub=0,
        vat_label=getattr(settings, "ZEMAZAP_VAT_LABEL", "НДС не задан"),
    )

    request_items = list(customer_request.items.select_related("part"))
    if request_items:
        for item in request_items:
            part = item.part
            OrderItem.objects.create(
                order=order,
                part=part,
                part_name=item.part_name,
                article=item.article,
                quantity=item.quantity,
                unit_price_rub=item.price_snapshot_rub,
                condition_snapshot=getattr(part, "condition", "") if part else "",
                fiscal_name=getattr(part, "fiscal_name", "") if part else "",
                vat_label=getattr(part, "vat_label", getattr(settings, "ZEMAZAP_VAT_LABEL", "НДС не задан"))
                if part
                else getattr(settings, "ZEMAZAP_VAT_LABEL", "НДС не задан"),
                payment_subject=getattr(part, "payment_subject", "commodity") if part else "commodity",
                payment_method=getattr(part, "payment_method", "full_payment") if part else "full_payment",
                unit=getattr(part, "unit", "шт.") if part else "шт.",
            )
    else:
        OrderItem.objects.create(
            order=order,
            part_name="Подбор по заявке",
            article="",
            quantity=1,
            unit_price_rub=0,
            vat_label=getattr(settings, "ZEMAZAP_VAT_LABEL", "НДС не задан"),
        )

    order.recalculate_total()
    OrderStatusHistory.objects.create(order=order, status=order.status, note="Order created from customer request.")
    return order, True
