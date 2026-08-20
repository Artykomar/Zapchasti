from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.customers.models import Customer

from .models import CustomerRequest


@transaction.atomic
def anonymize_customer_request(customer_request: CustomerRequest, *, reason: str = "") -> CustomerRequest:
    customer_request = CustomerRequest.objects.select_for_update().get(pk=customer_request.pk)
    if customer_request.anonymized_at:
        return customer_request

    customer_id = customer_request.customer_id
    marker = f"anon-request-{customer_request.pk}"
    customer_request.customer_name = "Удалено"
    customer_request.contact = marker
    customer_request.vehicle = ""
    customer_request.request_text = ""
    customer_request.consent_ip = None
    customer_request.consent_user_agent = ""
    customer_request.anonymized_at = timezone.now()
    customer_request.save(
        update_fields=[
            "customer_name",
            "contact",
            "vehicle",
            "request_text",
            "consent_ip",
            "consent_user_agent",
            "anonymized_at",
            "updated_at",
        ]
    )
    customer_request.events.update(note="")
    customer_request.events.create(event_type="personal_data_anonymized", note=reason[:500])

    if customer_id and not CustomerRequest.objects.filter(customer_id=customer_id, anonymized_at__isnull=True).exists():
        Customer.objects.filter(pk=customer_id).update(
            display_name="Удалено",
            contact=f"anon-customer-{customer_id}",
            normalized_contact=f"anon-customer-{customer_id}",
        )
    return customer_request
