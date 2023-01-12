from django.db import transaction
from rest_framework.generics import CreateAPIView

from .purchase_permissions import PurchaseReturnPermission
from .purchase_return_serializer import PurchaseReturnSerializer


class ReturnPurchaseView(CreateAPIView):
    permission_classes = [PurchaseReturnPermission]
    serializer_class = PurchaseReturnSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
