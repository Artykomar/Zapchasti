from django.urls import path

from .views import MockPaymentCallbackAPIView, PaymentLinkCreateAPIView

urlpatterns = [
    path("create-link/", PaymentLinkCreateAPIView.as_view(), name="payment-create-link"),
    path("mock/callback/", MockPaymentCallbackAPIView.as_view(), name="payment-mock-callback"),
]
