from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import permissions, viewsets
from django_filters.filterset import FilterSet
from django_filters import DateFromToRangeFilter, CharFilter
from src.supplier.models import Supplier
from log_app.serializers.supplier import SupplierHistorySerializer
from log_app.permissions.supplier_log_permissions import SupplierHistoryPermission


class FilterForSupplierHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    first_name = CharFilter(lookup_expr='iexact')
    class Meta:
        model = Supplier.history.model
        fields = ['id','history_type','history_date_bs']
        
class SupplierHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SupplierHistoryPermission]
    queryset = Supplier.history.all()
    serializer_class = SupplierHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForSupplierHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']