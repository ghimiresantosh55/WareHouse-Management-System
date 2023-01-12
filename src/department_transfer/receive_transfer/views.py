from django.db import transaction
from rest_framework.generics import CreateAPIView

from src.department_transfer.receive_transfer.serializers import ReceiveDepartmentTransferMasterSerializer


class ReceiveDepartmentTransferMasterView(CreateAPIView):
    serializer_class = ReceiveDepartmentTransferMasterSerializer


    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(ReceiveDepartmentTransferMasterView, self).create(request)
