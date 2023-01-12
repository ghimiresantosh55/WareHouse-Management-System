from django.db import transaction
from rest_framework.generics import CreateAPIView

from .customer_order_permissions import CustomerOrderPickupPermission, CustomerOrderPickupVerifyPermission
from .pickup_serializer import OrderPickupSerializer, VerifyOrderPickupSerializer


class CustomerOrderPickupViewSet(CreateAPIView):
    permission_classes = [CustomerOrderPickupPermission]
    serializer_class = OrderPickupSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class VerifyCustomerOrderPickupView(CreateAPIView):
    permission_classes = [CustomerOrderPickupVerifyPermission]
    serializer_class = VerifyOrderPickupSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
