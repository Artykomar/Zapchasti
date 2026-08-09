from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import CustomerRequest
from .serializers import CustomerRequestCreateSerializer
from .throttles import CustomerRequestRateThrottle


class CustomerRequestCreateAPIView(CreateAPIView):
    queryset = CustomerRequest.objects.all()
    serializer_class = CustomerRequestCreateSerializer
    throttle_classes = [CustomerRequestRateThrottle]
    throttle_scope = "customer_requests"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer_request = serializer.save()
        return Response(
            {
                "id": customer_request.id,
                "status": customer_request.status,
                "totalEstimateRub": customer_request.total_estimate_rub,
            },
            status=status.HTTP_201_CREATED,
        )

# Create your views here.
