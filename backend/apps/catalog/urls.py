from django.urls import path

from .views import CatalogDetailAPIView, CatalogListAPIView

urlpatterns = [
    path("", CatalogListAPIView.as_view(), name="catalog-list"),
    path("<slug:slug>/", CatalogDetailAPIView.as_view(), name="catalog-detail"),
]
