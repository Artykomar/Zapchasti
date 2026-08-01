from django.db import transaction
from rest_framework import serializers

from apps.catalog.models import Part
from apps.customers.models import Customer
from apps.notifications.services import notify_manager_about_request

from .models import CustomerRequest, CustomerRequestEvent, CustomerRequestItem


def normalize_contact(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    if len(digits) == 11 and digits.startswith("8"):
        return "7" + digits[1:]
    return digits or value.strip().lower()


class CustomerRequestItemInputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(max_length=240)
    article = serializers.CharField(max_length=120, required=False, allow_blank=True)
    quantity = serializers.IntegerField(min_value=1, max_value=99)
    price = serializers.IntegerField(min_value=0, required=False, default=0)


class CustomerRequestCreateSerializer(serializers.ModelSerializer):
    items = CustomerRequestItemInputSerializer(many=True, required=False)

    class Meta:
        model = CustomerRequest
        fields = [
            "id",
            "customer_name",
            "contact",
            "vehicle",
            "request_text",
            "source",
            "privacy_accepted",
            "total_estimate_rub",
            "items",
        ]
        read_only_fields = ["id", "total_estimate_rub"]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            aliases = {
                "customerName": "customer_name",
                "name": "customer_name",
                "requestText": "request_text",
                "message": "request_text",
                "parts": "request_text",
                "privacyAccepted": "privacy_accepted",
            }
            for source, target in aliases.items():
                if source in data and target not in data:
                    data[target] = data[source]
        return super().to_internal_value(data)

    def validate(self, attrs):
        items = attrs.get("items", [])
        if not attrs.get("request_text") and not items:
            raise serializers.ValidationError("Add request text or at least one cart item.")
        if not attrs.get("privacy_accepted"):
            raise serializers.ValidationError("Privacy consent is required.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("items", [])
        normalized_contact = normalize_contact(validated_data["contact"])
        customer, _created = Customer.objects.update_or_create(
            normalized_contact=normalized_contact,
            defaults={
                "display_name": validated_data["customer_name"],
                "contact": validated_data["contact"],
            },
        )
        total = sum(item.get("price", 0) * item["quantity"] for item in items)
        request = CustomerRequest.objects.create(
            customer=customer,
            total_estimate_rub=total,
            **validated_data,
        )

        for item in items:
            part = None
            if item.get("id"):
                part = Part.objects.filter(legacy_id=item["id"]).first()
                if not part:
                    part = Part.objects.filter(slug=item["id"]).first()
                if not part and item["id"].isdigit():
                    part = Part.objects.filter(id=int(item["id"])).first()
            CustomerRequestItem.objects.create(
                request=request,
                part=part,
                part_name=item["name"],
                article=item.get("article", ""),
                quantity=item["quantity"],
                price_snapshot_rub=item.get("price", 0),
            )

        CustomerRequestEvent.objects.create(
            request=request,
            event_type="created",
            note="Request created from Django API.",
        )
        transaction.on_commit(lambda: notify_manager_about_request(request))
        return request
