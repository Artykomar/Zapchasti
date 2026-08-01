from django.urls import path

from .views import PriceImportAPIView

urlpatterns = [
    path("prices/", PriceImportAPIView.as_view(), name="price-import"),
]
