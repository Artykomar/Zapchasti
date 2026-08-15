from django.urls import path

from .views import PublicOrderDetailAPIView

urlpatterns = [
    path("<uuid:token>/", PublicOrderDetailAPIView.as_view(), name="order-detail"),
]
