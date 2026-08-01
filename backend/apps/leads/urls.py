from django.urls import path

from .views import CustomerRequestCreateAPIView

urlpatterns = [
    path("", CustomerRequestCreateAPIView.as_view(), name="request-create"),
]
