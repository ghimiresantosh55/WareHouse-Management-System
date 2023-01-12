import django_filters
from django_filters import DateFromToRangeFilter
from django_filters.filterset import FilterSet
# filter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
# log imports
from simple_history.utils import update_change_reason

# permissions
from .core_app_permissions import SystemSetupPermission
from rest_framework.permissions import AllowAny

# importing of models
from .models import (AdditionalChargeType, AppAccessLog, Bank, BankDeposit, Country, DiscountScheme,
                     District, FiscalSessionAD, FiscalSessionBS, OrganizationRule, OrganizationSetup,
                     PaymentMode, Province, Store)
from .models import Currency
# importing of serializer
from .serializers import (AdditionalChargeTypeSerializer, AppAccessLogSerializer,
                          BankDepositCreateSerializer, BankDepositViewSerializer, BankSerializer,
                          CountrySerializer, DiscountSchemeSerializer, DistrictSerializer,
                          FiscalSessionADSerializer, FiscalSessionBSSerializer, OrganizationRuleSerializer,
                          OrganizationSetupSerializer, PaymentModeSerializer, ProvinceSerializer,
                          StoreSerializer, PaymentModeCoreSerializer)
from .serializers import CurrencySerializer
from .setup_helper import check_setup


class PaymentModeAPIListView(ListAPIView):
    queryset = PaymentMode.objects.filter(active=True)
    serializer_class = PaymentModeCoreSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class FilterForCountry(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Country
        fields = ['name', 'country_code']


class CountryViewSet(viewsets.ModelViewSet):
    # addition of permission
    permission_classes = [SystemSetupPermission]
    # objects.all() helps to get all the object from table (i.e. model)
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    # helps to control http method
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForCountry
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def partial_update(self, request, *args, **kwargs):
        # exception handling
        # first try block is executed if condition doesnot match error is passed.
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            # after checking of validation data is passed into purchase_order_serializer
            serializer.save()

            # for log history. Atleast one reason must be given if update is made. Atleast one reason must be given if update is made Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForCurrency(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Currency
        fields = ['name', 'code']


class CurrencyViewSet(viewsets.ModelViewSet):
    # addition of permission
    permission_classes = [SystemSetupPermission]
    # objects.all() helps to get all the object from table (i.e. model)
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    # helps to control http method
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForCurrency
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def partial_update(self, request, *args, **kwargs):
        # exception handling
        # first try block is executed if condition doesnot match error is passed.
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            # after checking of validation data is passed into purchase_order_serializer
            serializer.save()

            # for log history. Atleast one reason must be given if update is made. Atleast one reason must be given if update is made Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForProvince(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Province
        fields = ['name', ]


class ProvinceViewset(viewsets.ModelViewSet):
    # addition of permission
    permission_classes = [SystemSetupPermission]

    # objects.all() helps to get all the object from table (i.e. model)
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    # helps to control http method
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForProvince
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForDistrict(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = District
        fields = ['name', ]


class DistrictViewset(viewsets.ModelViewSet):
    # addition of permission
    permission_classes = [SystemSetupPermission]
    # objects.all() helps to get all the object from table (i.e. model)
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    # helps to control http method
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForDistrict
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def partial_update(self, request, *args, **kwargs):
        # exception handling
        # first try block is executed if condition doesnot match error is passed.
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationRuleViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = OrganizationRule.objects.all()
    serializer_class = OrganizationRuleSerializer
    http_method_names = ['get', 'head', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        # exception handling
        # first try block is executed if condition doesnot match error is passed.
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationSetupViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = OrganizationSetup.objects.all().select_related("country")
    serializer_class = OrganizationSetupSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name', 'address', 'email', 'created_date_ad']
    filter_fields = ['name', 'address', 'email', 'created_date_ad']
    search_fields = ['name', 'address', 'email', 'created_date_ad']

    def partial_update(self, request, *args, **kwargs):
        # exception handling
        # first try block is executed if condition doesnot match error is passed.
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# for filter using date range
class FilterForBank(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    # iexact is used for Case-insensitive exact match in search field. Nepal and nepaL are same
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Bank
        fields = ['active']


class BankViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForBank
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# custom filter for bank model
class FilterForBankDepositMaster(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = BankDeposit
        fields = ['date', 'bank__name', 'deposit_by', 'amount', 'created_by__user_name']


class BankDepositViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = BankDeposit.objects.all().select_related("bank")
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_class = FilterForBankDepositMaster
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'bank', 'deposit_by', 'amount', 'deposit_date_bs', 'deposit_date_ad']
    search_fields = ['bank__name', 'amount', 'remarks', 'deposit_by', 'created_by__user_name']

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            serializer_class = BankDepositCreateSerializer
        elif self.request.method == 'GET':
            serializer_class = BankDepositViewSerializer
        return serializer_class

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()

            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForPaymentMode(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = PaymentMode
        fields = ['active']


class PaymentModeViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = PaymentMode.objects.all()
    serializer_class = PaymentModeSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name']
    filter_class = FilterForPaymentMode
    search_fields = ['name', 'remarks']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()

            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForDiscountScheme(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = DiscountScheme
        fields = ['active', 'editable']


class DiscountSchemeViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = DiscountScheme.objects.all()
    serializer_class = DiscountSchemeSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name']
    filter_class = FilterForDiscountScheme
    search_fields = ['name']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForAdditionalChargeType(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = AdditionalChargeType
        fields = ['active']


class AdditionalChargeTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = AdditionalChargeType.objects.all()
    serializer_class = AdditionalChargeTypeSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name']
    filter_class = FilterForAdditionalChargeType
    search_fields = ['name']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()

            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForAppAccessLog(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = AppAccessLog
        fields = "__all__"


class AppAccessLogViewset(viewsets.ModelViewSet):
    queryset = AppAccessLog.objects.all()
    # permission_classes = [AppAccessLogPermission]
    serializer_class = AppAccessLogSerializer
    http_method_names = ['get', 'head', 'post']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForAppAccessLog
    ordering_fields = ['id']
    search_fields = ['app_type', 'device_type']


class FilterForStore(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Store
        fields = ['active', 'name']


class StoreViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name']
    filter_class = FilterForStore
    search_fields = ['name', 'code']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()

            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForFiscalSessionAD(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = FiscalSessionAD
        fields = ['session_full', 'session_short']


class FiscalSessionADViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = FiscalSessionAD.objects.all()
    serializer_class = FiscalSessionADSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name']
    filter_class = FilterForFiscalSessionAD
    search_fields = ['session_full', 'session_short']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()

            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForFiscalSessionBS(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = FiscalSessionBS
        fields = ['session_full', 'session_short']


class FiscalSessionBSViewSet(viewsets.ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = FiscalSessionBS.objects.all()
    serializer_class = FiscalSessionBSSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'name']
    filter_class = FilterForFiscalSessionBS
    search_fields = ['session_full', 'session_short']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()

            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetupInfoView(APIView):
    def get(self, request):
        return Response({'is_setup_done': check_setup()}, status=status.HTTP_200_OK)
