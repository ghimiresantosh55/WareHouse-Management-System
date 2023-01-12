from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from rest_framework import viewsets
from django_filters.filterset import FilterSet
from src.sale.models import SaleMaster, SaleDetail, SalePaymentDetail, SaleAdditionalCharge,\
    SalePrintLog
from log_app.serializers.sale import * 
# permission
from log_app.permissions.sale_log_permissions import SaleMasterHistoryPermission, SaleDetailHistoryPermission,\
    SaleAdditionalChargeHistoryPermission, SalePaymentDetailHistoryPermission,\
        SalePrintLogHistoryPermission 


class FilterForSaleMasterHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = SaleMaster.history.model
        fields = ['id','history_type','history_date_bs']

class SaleMasterHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleMasterHistoryPermission]
    queryset = SaleMaster.history.all()
    serializer_class = SaleMasterHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForSaleMasterHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForSaleDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = SaleDetail.history.model
        fields = ['id','history_type','history_date_bs']

class SaleDetailHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleDetailHistoryPermission]
    queryset = SaleDetail.history.all()
    serializer_class = SaleDetailHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForSaleDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForSalePaymentDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    # name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = SalePaymentDetail.history.model
        fields = ['id','history_type','history_date_bs']
        
class SalePaymentDetailHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SalePaymentDetailHistoryPermission]
    queryset = SalePaymentDetail.history.all()
    serializer_class = SalePaymentDetailHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForSalePaymentDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForSaleAdditionalChargeHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = SaleAdditionalCharge.history.model
        fields = ['id','history_type','history_date_bs']

class SaleAdditionalChargeHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleAdditionalChargeHistoryPermission]
    queryset = SaleAdditionalCharge.history.all()
    serializer_class = SaleAdditionalChargeHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForSaleAdditionalChargeHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForSalePrintLogHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = SalePrintLog.history.model
        fields = ['id','history_type','history_date_bs']

class SalePrintLogHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SalePrintLogHistoryPermission]
    queryset = SalePrintLog.history.all()
    serializer_class = SalePrintLogHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForSalePrintLogHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

