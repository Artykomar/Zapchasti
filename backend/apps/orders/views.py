from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import Order
from .serializers import OrderPublicSerializer


class PublicOrderDetailAPIView(RetrieveAPIView):
    queryset = Order.objects.prefetch_related("items", "payments")
    serializer_class = OrderPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = "token"
    lookup_url_kwarg = "token"
