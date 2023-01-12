from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from rest_framework import viewsets
from django_filters.filterset import FilterSet
from src.credit_management.models import *
from log_app.serializers.credit_management import CreditClearanceHistorySerializer, CreditPaymentDetailHistorySerializer
from log_app.permissions.credit_management_log_permissions import CreditClearanceHistoryPermission,\
    CreditPaymentDetailHistoryPermission


class FilterForCreditClearanceHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = CreditClearance.history.model
        fields = ['id','history_type','history_date_bs']

class CreditClearanceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditClearanceHistoryPermission]
    queryset = CreditClearance.history.all()
    serializer_class = CreditClearanceHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForCreditClearanceHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForCreditPaymentDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = CreditPaymentDetail.history.model
        fields = ['id','history_type','history_date_bs']

class CreditPaymentDetailHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditPaymentDetailHistoryPermission]
    queryset = CreditPaymentDetail.history.all()
    serializer_class = CreditPaymentDetailHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForCreditPaymentDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

