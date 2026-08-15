from rest_framework import serializers

from .models import Payment


class PaymentLinkSerializer(serializers.ModelSerializer):
    order_token = serializers.UUIDField(source="order.token", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "public_id",
            "order_token",
            "provider",
            "mode",
            "status",
            "amount_rub",
            "currency",
            "bank_order_id",
            "form_url",
        ]
