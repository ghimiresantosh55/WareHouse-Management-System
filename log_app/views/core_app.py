from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from rest_framework import permissions, viewsets
from django_filters.filterset import FilterSet
from rest_framework.settings import perform_import
from src.core_app.models import AdditionalChargeType, AppAccessLog, BankDeposit,\
    Bank, Country, DiscountScheme, District, OrganizationRule, OrganizationSetup,\
        PaymentMode, Province
from log_app.serializers.core_app import *
from log_app.permissions.core_app_log_permissions import *


class FilterForCountryHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = Country.history.model
        fields = ['id','history_type','history_date_bs']

class CountryHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CountryHistoryPermission]
    queryset = Country.history.all()
    serializer_class = CountryHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForCountryHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForProvinceHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = Province.history.model
        fields = ['id','history_type','history_date_bs']

class ProvinceHistoryViewset(viewsets.ModelViewSet):
    permission_classes = [ProvinceHistoryPermission]
    queryset = Province.history.all()
    serializer_class = ProvinceHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForProvinceHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForDistrictHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = District.history.model
        fields = ['id','history_type','history_date_bs']

class DistrictHistoryViewset(viewsets.ModelViewSet):
    permission_classes = [DistrictHistoryPermission]
    queryset = District.history.all()
    serializer_class = DistrictHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForDistrictHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForOrganizationRuleHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = OrganizationRule.history.model
        fields = ['id','history_type','history_date_bs']

class OrganizationRuleHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [OrganizationRuleHistoryPermission]
    queryset = OrganizationRule.history.all()
    serializer_class = OrganizationRuleHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForOrganizationRuleHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForOrganizationSetupHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = OrganizationSetup.history.model
        fields = ['id','history_type','history_date_bs']

    
class OrganizationSetupHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [OrganizationSetupHistoryPermission]
    queryset = OrganizationSetup.history.all()
    serializer_class = OrganizationSetupHistorySerializer
    http_method_names = ['get', 'head','option']
    filter_class = FilterForOrganizationSetupHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForBankHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = Bank.history.model
        fields = ['id','history_type','history_date_bs']

class BankHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [BankHistoryPermission]
    queryset = Bank.history.all()
    serializer_class = BankHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForBankHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForBankDepositHistory(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = BankDeposit.history.model
        fields = ['id','history_type','history_date_bs']

class BankDepositHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [BankDepositHistoryPermission]
    queryset = BankDeposit.history.all()
    serializer_class = BankDepositHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForBankDepositHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForPaymentModeHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = PaymentMode.history.model
        fields = ['id','history_type','history_date_bs']

class PaymentModeHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [PaymentModeHistoryPermission]
    queryset = PaymentMode.history.all()
    serializer_class = PaymentModeHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForPaymentModeHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForDiscountSchemeHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = DiscountScheme.history.model
        fields = ['id','history_type','history_date_bs']

class DiscountSchemeHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [DiscountSchemeHistoryPermission]
    queryset = DiscountScheme.history.all()
    serializer_class = DiscountSchemeHistorySerializer
    http_method_names = ['get', 'head','option']
    filter_class = FilterForDiscountSchemeHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForAdditionalChargeTypeHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = AdditionalChargeType.history.model
        fields = ['id','history_type','history_date_bs']


class AdditionalChargeTypeHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AdditionalChargeTypeHistoryPermission]
    queryset = AdditionalChargeType.history.all()
    serializer_class = AdditionalChargeTypeHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForAdditionalChargeTypeHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForAppAccessLogHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = AppAccessLog.history.model
        fields = ['id','history_type','history_date_bs']

class AppAccessLogHistoryViewset(viewsets.ModelViewSet):
    permission_classes = [AppAccessLogHistoryPermission]
    queryset = AppAccessLog.history.all()
    serializer_class = AppAccessLogHistorySerializer
    http_method_names = ['get', 'head', 'option']
    filter_class = FilterForAppAccessLogHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']
   

