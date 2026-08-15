from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["part_name", "article", "quantity", "unit_price_rub", "line_total_rub"]


class OrderPublicSerializer(serializers.ModelSerializer):
    items = OrderItemPublicSerializer(many=True, read_only=True)
    payment_allowed = serializers.BooleanField(source="can_create_payment", read_only=True)
    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "token",
            "status",
            "customer_name",
            "vehicle",
            "currency",
            "total_amount_rub",
            "delivery_terms",
            "warranty_terms",
            "vat_label",
            "payment_allowed",
            "payment_url",
            "items",
        ]

    def get_payment_url(self, order: Order) -> str:
        payment = order.payments.filter(status="pending").first()
        return payment.form_url if payment else ""
