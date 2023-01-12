from rest_framework import viewsets
from .models import AdvancedDeposit
from .advance_deposite_permissions import AdvancedDepositSavePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .serializers import SaveAdvancedDepositSerializer

class SaveAdvancedDepositViewSet(viewsets.ModelViewSet):
    permission_classes = [AdvancedDepositSavePermission]
    queryset = AdvancedDeposit.objects.all().select_related("order_master","sale_master")
    http_method_names = ['post', 'get']
    serializer_class = SaveAdvancedDepositSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['remarks']
    filter_fields = ['order_master', 'sale_master']
    ordering_fields = ['id','order_master', 'sale_master', 'deposit_no']