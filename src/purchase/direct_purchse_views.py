from django.db import transaction
from rest_framework.generics import CreateAPIView

from .direct_purchase_serializer import DirectPurchaseMasterCreateSerializer


class DirectPurchaseCreateView(CreateAPIView):
    serializer_class = DirectPurchaseMasterCreateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(DirectPurchaseCreateView, self).create(request, args, kwargs)
