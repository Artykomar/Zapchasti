from django.urls import path

from .views import (
    AlfaPaymentCallbackAPIView,
    MockPaymentCallbackAPIView,
    PaymentLinkCreateAPIView,
    PaymentStatusRefreshAPIView,
)

urlpatterns = [
    path("create-link/", PaymentLinkCreateAPIView.as_view(), name="payment-create-link"),
    path("mock/callback/", MockPaymentCallbackAPIView.as_view(), name="payment-mock-callback"),
    path("refresh-status/", PaymentStatusRefreshAPIView.as_view(), name="payment-refresh-status"),
    path("alfa/callback/", AlfaPaymentCallbackAPIView.as_view(), name="payment-alfa-callback"),
]
