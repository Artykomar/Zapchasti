from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order

from .models import Payment
from .serializers import PaymentLinkSerializer
from .services import apply_mock_payment_callback, create_payment_link_for_order


class PaymentLinkCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        order_id = request.data.get("orderId")
        order_token = request.data.get("orderToken")
        try:
            if order_token:
                order = Order.objects.get(token=order_token)
            else:
                order = Order.objects.get(pk=order_id)
        except (ObjectDoesNotExist, ValueError, TypeError):
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            payment = create_payment_link_for_order(order)
        except ValidationError as exc:
            return Response({"error": "; ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PaymentLinkSerializer(payment).data, status=status.HTTP_201_CREATED)


class MockPaymentCallbackAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        public_id = request.data.get("publicId") or request.data.get("paymentId")
        mock_status = request.data.get("status", "")
        if not public_id:
            return Response({"error": "publicId is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = apply_mock_payment_callback(public_id, mock_status)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            return Response({"error": "; ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PaymentLinkSerializer(payment).data)
