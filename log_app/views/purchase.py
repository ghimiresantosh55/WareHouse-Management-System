from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from rest_framework import viewsets
from django_filters.filterset import FilterSet
from src.purchase.models import PurchaseOrderMaster, PurchaseOrderDetail,\
    PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge
from log_app.serializers.purchase import PurchaseOrderMasterHistorySerializer, PurchaseOrderDetailHistorySerializer,\
         PurchaseMasterHistorySerializer, PurchaseDetailHistorySerializer,PurchasePaymentDetailHistorySerializer,\
             PurchaseAdditionalChargeHistorySerializer
from log_app.permissions.purchase_log_permissions import PurchaseOrderMasterHistoryPermission,\
    PurchaseOrderDetailHistoryPermission, PurchaseMasterHistoryPermission,\
        PurchaseDetailHistoryPermission, PurchaseAdditionalChargeHistoryPermission,\
            PurchasePaymentDetailHistoryPermission


class FilterForPurchaseOrderMasterHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = PurchaseOrderMaster.history.model
        fields = ['id','history_type','history_date_bs']

class PurchaseOrderMasterHistroyViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderMasterHistoryPermission]
    queryset = PurchaseOrderMaster.history.all()
    serializer_class = PurchaseOrderMasterHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPurchaseOrderMasterHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForPurchaseOrderDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = PurchaseOrderDetail.history.model
        fields = ['id','history_type','history_date_bs']

class PurchaseOrderDetailHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderDetailHistoryPermission]
    queryset = PurchaseOrderDetail.history.all()
    serializer_class = PurchaseOrderDetailHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class =  FilterForPurchaseOrderDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForPurchaseMasterHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = PurchaseMaster.history.model
        fields = ['id','history_type','history_date_bs']

class PurchaseMasterHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseMasterHistoryPermission]
    queryset = PurchaseMaster.history.all()
    serializer_class = PurchaseMasterHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPurchaseMasterHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForPurchaseDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    # name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = PurchaseDetail.history.model
        fields = ['id','history_type','history_date_bs']

class PurchaseDetailHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseDetailHistoryPermission]
    queryset = PurchaseDetail.history.all()
    serializer_class = PurchaseDetailHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPurchaseDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForPurchasePaymentDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    # name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = PurchasePaymentDetail.history.model
        fields = ['id','history_type','history_date_bs']

class PurchasePaymentDetailHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchasePaymentDetailHistoryPermission]
    queryset = PurchasePaymentDetail.history.all()
    serializer_class = PurchasePaymentDetailHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPurchasePaymentDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForPurchaseAdditionalChargeHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    # name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = PurchaseAdditionalCharge.history.model
        fields = ['id','history_type','history_date_bs']

class PurchaseAdditionalChargeHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseAdditionalChargeHistoryPermission]
    queryset = PurchaseAdditionalCharge.history.all()
    serializer_class = PurchaseAdditionalChargeHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPurchaseAdditionalChargeHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']
    
