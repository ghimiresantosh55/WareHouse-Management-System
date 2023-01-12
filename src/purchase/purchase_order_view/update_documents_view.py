from django.db import transaction
from rest_framework.generics import CreateAPIView

from ..purchase_order_serializer.update_documents_serializer import AddPurchaseDocumentsSerializer, \
    AddPurchaseOrderDocumentsSerializer


class AddPurchaseOrderDocumentsView(CreateAPIView):
    serializer_class = AddPurchaseOrderDocumentsSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(AddPurchaseOrderDocumentsView, self).create(request, *args, **kwargs)


class AddPurchaseDocumentsView(CreateAPIView):
    serializer_class = AddPurchaseDocumentsSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(AddPurchaseDocumentsView, self).create(request, *args, **kwargs)
