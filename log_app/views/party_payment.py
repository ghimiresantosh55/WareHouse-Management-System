from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from rest_framework import viewsets
from django_filters.filterset import FilterSet
from src.party_payment.models import  PartyPayment, PartyPaymentDetail
from log_app.serializers.party_payment import PartyPaymentHistorySerializer, PartyPaymentDetailHistorySerializer
from log_app.permissions.party_payment_log_permissions import PartyClearanceHistoryPermission, PartyPaymentDetailHistoryPermission

class FilterForPartyPaymentHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    # name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = PartyPayment.history.model
        fields = ['id','history_type','history_date_bs']

class PartyClearanceHistroyViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyClearanceHistoryPermission]
    queryset = PartyPayment.history.all()
    serializer_class = PartyPaymentHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPartyPaymentHistory
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

class FilterForPartyPaymentDetailHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = PartyPaymentDetail.history.model
        fields = ['id','history_type','history_date_bs']

class PartyPaymentDetailHistroyViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentDetailHistoryPermission]
    queryset = PartyPaymentDetail.history.all()
    serializer_class = PartyPaymentDetailHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPartyPaymentDetailHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

