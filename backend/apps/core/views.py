from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import build_public_site_settings


class PublicSiteSettingsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(build_public_site_settings())
