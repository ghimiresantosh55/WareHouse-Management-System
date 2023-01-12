from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from rest_framework import permissions, viewsets
from django_filters.filterset import FilterSet
from src.customer_order.models import OrderMaster,OrderDetail
from log_app.serializers.customer_order import OrderMasterHistorySerializer, OrderDetailHistorySerializer
from log_app.permissions.customer_order_log_permissions import CustomerOrderMasterHistoryPermission,\
    CustomerOrderDetailHistoryPermission


class FilterForOrderMasterHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = OrderMaster.history.model
        fields = ['id','history_type','history_date_bs']

class OrderMasterHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderMasterHistoryPermission]
    queryset = OrderMaster.history.all()
    serializer_class = OrderMasterHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForOrderMasterHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']
    

class FilterForOrderDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = OrderDetail.history.model
        fields = ['id','history_type','history_date_bs']

class OrderDetailHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderDetailHistoryPermission]
    queryset = OrderDetail.history.all()
    serializer_class = OrderDetailHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForOrderDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

