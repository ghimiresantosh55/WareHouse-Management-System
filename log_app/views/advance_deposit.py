from django.db.models.fields import DateField, DateTimeField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import DateFromToRangeFilter
from rest_framework import viewsets
from django_filters.filterset import FilterSet
from src.advance_deposit.models import AdvancedDeposit, AdvancedDepositPaymentDetail
from log_app.serializers.advance_deposit import AdvancedDepositHistorySerializer, AdvancedDepositPaymentDetailHistorySerializer
from log_app.permissions.advance_deposite_log_permissions import AdvanceDepositHistoryPermission, AdvanceDepositPaymentDetailHistoryPermission


class FilterForAdvancedDepositHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    
    class Meta:
        model = AdvancedDeposit.history.model
        fields = ['id','history_type','history_date_bs']


class AdvancedDepositHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes =  [AdvanceDepositHistoryPermission]
    queryset = AdvancedDeposit.history.all()
    serializer_class = AdvancedDepositHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForAdvancedDepositHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForAdvancedDepositPaymentDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = AdvancedDepositPaymentDetail.history.model
        fields = ['id','history_type','history_date_bs']

class AdvancedDepositPaymentDetailHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes =  [AdvanceDepositPaymentDetailHistoryPermission]
    queryset = AdvancedDepositPaymentDetail.history.all()
    http_method_names = ['get','head', 'option']
    serializer_class = AdvancedDepositPaymentDetailHistorySerializer
    filter_class = FilterForAdvancedDepositPaymentDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']