import django_filters
from django.db import transaction
from django.db.models import Window, F, Sum, Subquery, OuterRef, CharField
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Account, AccountGroup, VoucherMaster
from .models import VoucherDetail
from .serializers import AccountGroupSaveSerializer, SaveAccountSerializer, SaveVoucherMasterSerializer, \
    AccountListSerializer, AccountGroupSerializer, VoucherMasterListSerializer, VoucherSummarySerializer, \
    AccountLedgerSerializer, AccountGroupTreeSerializer, ProfitAndLossReportSerializer, BalanceSheetSerializer


# from djangorestframework_camel_case.parser import CamelCaseMultiPartParser


# Create your views here.

def ledger_view(request):
    accounts = Account.objects.all()
    return render(request, 'ledger.html', {'accounts': accounts})


def ledger_detail_view(request, account_id):
    ref_account = VoucherDetail.objects.filter(voucher_master=OuterRef('voucher_master')).exclude(
        id=OuterRef('id')).annotate(
        ref_name=F('account__name')).values(
        "ref_name")[:1]

    ledger = VoucherDetail.objects.filter(account=account_id).annotate(differ=F('dr_amount') - F('cr_amount'),
                                                                       ref_account=Subquery(ref_account,
                                                                                            output_field=CharField())).annotate(
        balance=Window(
            expression=
            Sum('differ'),
            order_by=F('id').asc()
        )
    )
    account = Account.objects.get(id=account_id)
    return render(request, 'ledger_detail.html', {'ledger': ledger, 'account': account})


class FilterForAccountGroup(django_filters.FilterSet):
    # for date range filter after_date and before_date
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    # iexact is used for Case-insensitive exact match in search field. Nepal and nEpaL are same
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = AccountGroup
        fields = ['date', 'name']


class AccountGroupViewSet(ModelViewSet):
    queryset = AccountGroup.objects.all()
    http_method_names = ['post', 'get', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['id', 'created_date_ad']
    filterset_class = FilterForAccountGroup

    def get_serializer_class(self):

        if self.request.method == "GET":
            return AccountGroupSerializer
        else:
            return AccountGroupSaveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(AccountGroupViewSet, self).create(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(AccountGroupViewSet, self).partial_update(request, *args, **kwargs)


class FilterForAccount(django_filters.FilterSet):
    # for date range filter after_date and before_date
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    # iexact is used for Case-insensitive exact match in search field. Nepal and nEpaL are same
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Account
        fields = ['date', 'group', 'name']


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = SaveAccountSerializer
    http_method_names = ['post', 'get', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['id', 'created_date_ad']
    filterset_class = FilterForAccount

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return SaveAccountSerializer
        else:
            return AccountListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(AccountViewSet, self).create(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(AccountViewSet, self).partial_update(request, *args, **kwargs)


class SaveVoucherView(CreateAPIView):
    serializer_class = SaveVoucherMasterSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(SaveVoucherView, self).create(request, *args, **kwargs)


class VoucherMasterViewSet(ListAPIView):
    serializer_class = VoucherMasterListSerializer
    queryset = VoucherMaster.objects.all()
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['narration']
    ordering_fields = ['id', 'created_date_ad']


class VoucherSummaryViewSet(RetrieveAPIView):
    serializer_class = VoucherSummarySerializer
    queryset = VoucherMaster.objects.all()


class FilterForAccountLedger(django_filters.FilterSet):
    # for date range filter after_date and before_date
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    # iexact is used for Case-insensitive exact match in search field. Nepal and nEpaL are same
    name = django_filters.CharFilter(lookup_expr='iexact')
    group = django_filters.ModelMultipleChoiceFilter(
        queryset=AccountGroup.objects.all(), to_field_name="id"
    )
    id = django_filters.ModelMultipleChoiceFilter(
        queryset=Account.objects.all(), to_field_name="id"
    )

    class Meta:
        model = Account
        fields = ['date', 'group', 'name', 'id']


class AccountLedgerView(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountLedgerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FilterForAccountLedger


class FilterForAccountGroupTree(django_filters.FilterSet):
    # for date range filter after_date and before_date
    id = django_filters.ModelMultipleChoiceFilter(
        queryset=AccountGroup.objects.all(), to_field_name="id"
    )
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')

    class Meta:
        model = AccountGroup
        fields = ['id', 'date']


class AccountGroupTreeView(ListAPIView):
    queryset = AccountGroup.objects.all()
    serializer_class = AccountGroupTreeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FilterForAccountGroupTree


class FilterForProfitLossReport(django_filters.FilterSet):
    # for date range filter after_date and before_date
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = AccountGroup
        fields = ['date']


class ProfitAndLossReportView(ListAPIView):
    groups = ["Direct Income", "Indirect Income", "Direct Expenses", "Indirect Expenses"]
    queryset = AccountGroup.objects.filter(name__in=groups)
    filter_backends = [DjangoFilterBackend]
    serializer_class = ProfitAndLossReportSerializer
    filterset_class = FilterForProfitLossReport

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BalanceSheetViewView(ListAPIView):
    groups = ["Asset", "Liabilities", "Equity"]
    queryset = AccountGroup.objects.filter(name__in=groups)
    filter_backends = [DjangoFilterBackend]
    serializer_class = BalanceSheetSerializer
    filterset_class = FilterForProfitLossReport

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        data['Reserve and Surplus'] = self.calculate_reserve_surplus()
        return Response(data)

    def calculate_reserve_surplus(self):
        request = self.context.get("request")
        query_parameters = request.query_params
        date_after = ""
        date_before = ""
        if 'date_after' in query_parameters:
            date_after = query_parameters['date_after']

        if 'date_before' in query_parameters:
            date_before = query_parameters['date_before']
        # Calculate Income
        instance = AccountGroup.objects.get(name="Income")
        groups = instance.get_descendants(include_self=True).values_list('id', flat=True)
        accounts = Account.objects.filter(group__in=groups).values_list('id', flat=True)
        voucher_details = VoucherDetail.objects.all()
        if date_after:
            voucher_details = voucher_details.filter(created_date_ad__date__gte=date_after)
        if date_before:
            voucher_details = voucher_details.filter(created_date_ad__date__lte=date_before)
        total_income_credit = sum(voucher_details.filter(account__in=accounts).values_list('cr_amount', flat=True))
        total_income_debit = sum(voucher_details.filter(account__in=accounts).values_list('dr_amount', flat=True))

        income = total_income_debit - total_income_credit

        # calculate expenses
        instance = AccountGroup.objects.get(name="Expenses")
        groups = instance.get_descendants(include_self=True).values_list('id', flat=True)
        accounts = Account.objects.filter(group__in=groups).values_list('id', flat=True)
        voucher_details = VoucherDetail.objects.all()
        if date_after:
            voucher_details = voucher_details.filter(created_date_ad__date__gte=date_after)
        if date_before:
            voucher_details = voucher_details.filter(created_date_ad__date__lte=date_before)
        total_expenses_credit = sum(voucher_details.filter(account__in=accounts).values_list('cr_amount', flat=True))
        total_expenses_debit = sum(voucher_details.filter(account__in=accounts).values_list('dr_amount', flat=True))

        expenses = total_expenses_debit - total_expenses_credit

        return income - expenses
