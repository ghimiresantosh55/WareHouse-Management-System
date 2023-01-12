import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView

from src.account.listing_apis.serializers import AccountGroupListSerializer, VoucherAccountListSerializer
from src.account.models import AccountGroup, Account


class FilterForAccount(django_filters.FilterSet):
    # for date range filter after_date and before_date
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    group = django_filters.ModelMultipleChoiceFilter(queryset=AccountGroup.objects.all(),
                                                     to_field_name='id')

    # iexact is used for Case-insensitive exact match in search field. Nepal and nEpaL are same
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Account
        fields = ['date', 'group', 'name']


class FilterForAccountGroup(django_filters.FilterSet):
    # for date range filter after_date and before_date
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    # iexact is used for Case-insensitive exact match in search field. Nepal and nEpaL are same
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = AccountGroup
        fields = ['date', 'name']


class AccountGroupListViewSet(ListAPIView):
    serializer_class = AccountGroupListSerializer
    queryset = AccountGroup.objects.all()
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['id', 'created_date_ad']
    filterset_class = FilterForAccountGroup


class AccountListViewSet(ListAPIView):
    serializer_class = VoucherAccountListSerializer
    queryset = Account.objects.all()
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['id', 'created_date_ad']
    filterset_class = FilterForAccount
