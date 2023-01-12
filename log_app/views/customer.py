from log_app.serializers.customer import CustomerHistoryListView
from src.customer.models import Customer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets
from django_filters.filterset import FilterSet
from django_filters import DateFromToRangeFilter
from log_app.permissions.customer_log_permissions import CustomerHistoryPermission


class FilterForCustomerHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = Customer.history.model
        fields = ['id','history_type','history_date_bs']

class CustomerHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerHistoryPermission]
    queryset= Customer.history.all()
    serializer_class = CustomerHistoryListView
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForCustomerHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']