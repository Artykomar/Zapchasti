from django.urls import path

from .views import PublicSiteSettingsAPIView

urlpatterns = [
    path("site-settings/", PublicSiteSettingsAPIView.as_view(), name="site-settings"),
]
