import secrets

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order

from .models import Payment
from .serializers import PaymentLinkSerializer
from .services import apply_mock_payment_callback, create_payment_link_for_order, synchronize_payment_status


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


class PaymentStatusRefreshAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        public_id = request.data.get("publicId") or request.data.get("paymentId")
        try:
            payment = Payment.objects.get(public_id=public_id)
            payment = synchronize_payment_status(payment)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        except (ValidationError, ValueError, TypeError) as exc:
            message = "; ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc)
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PaymentLinkSerializer(payment).data)


class AlfaPaymentCallbackAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        configured_token = str(getattr(settings, "ALFA_BANK_CALLBACK_TOKEN", ""))
        supplied_token = str(request.query_params.get("token", ""))
        if not configured_token or not secrets.compare_digest(configured_token, supplied_token):
            return Response({"error": "Invalid callback token."}, status=status.HTTP_403_FORBIDDEN)

        bank_order_id = request.data.get("orderId") or request.data.get("mdOrder")
        try:
            payment = Payment.objects.get(bank_order_id=bank_order_id)
            payment = synchronize_payment_status(payment)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            return Response({"error": "; ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": payment.status})
