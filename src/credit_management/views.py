# filter
import django_filters
from django.db import transaction
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from src.custom_lib.functions.credit_management import get_sale_credit_detail
from src.customer.models import Customer
from src.customer.serializers import CustomerSerializer
# importing of models
from src.sale.models import SaleMaster
from .credit_clearance_serializer import SaveCreditClearanceSerializer
# custom permissions
from .credit_management_permissions import CreditManagementPermission
from .models import CreditClearance, CreditPaymentDetail
# functions
# importing of serializer
from .serializers import CreditPaymentMasterSerializer, CreditPaymentDetailSerializer, SaleCreditSerializer


# Create your views here.
class RangeFilterForCreditClearance(django_filters.FilterSet):
    # for date range filter
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = CreditClearance
        fields = '__all__'


class CreditClearanceViewSet(viewsets.ReadOnlyModelViewSet):
    # permissions
    permission_classes = [CreditManagementPermission]
    queryset = CreditClearance.objects.all().select_related("sale_master", "ref_credit_clearance",
                                                            'sale_master__customer')
    serializer_class = CreditPaymentMasterSerializer
    filter_class = RangeFilterForCreditClearance
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = ['id']
    ordering_fields = ['id']


class CreditPaymentDetailFilterSet(django_filters.FilterSet):
    sale_master = django_filters.NumberFilter(field_name='credit_clearance__sale_master')

    class Meta:
        model = CreditPaymentDetail
        fields = ['id', 'sale_master']


class CreditPaymentDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditManagementPermission]
    queryset = CreditPaymentDetail.objects.all().select_related("credit_clearance", "payment_mode")
    serializer_class = CreditPaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = CreditPaymentDetailFilterSet
    ordering_fields = ['credit_clearance', 'id']


class CreditClearanceSummary(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditManagementPermission]
    queryset = CreditClearance.objects.all().select_related("sale_master", "ref_credit_clearance")
    serializer_class = SaveCreditClearanceSerializer
    filter_class = RangeFilterForCreditClearance
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)


class FilterForCreditReportSaleMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'created_by', 'created_date_ad', 'sale_type', 'customer']


class GetCreditInvoice(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditManagementPermission]
    queryset = SaleMaster.objects.filter(pay_type=2).select_related("discount_scheme", "customer", "ref_order_master")
    serializer_class = SaleCreditSerializer
    filter_class = FilterForCreditReportSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no']
    ordering_fields = ['id', 'sale_id', 'created_date_ad']

    @action(detail=False, methods=['GET'])
    def customers(self, request):
        data = get_sale_credit_detail()
        id_list = data.values_list('customer', flat=True)
        # converting a list into set for removing repeated values
        customer_id_list = set(id_list)
        customers = Customer.objects.filter(id__in=customer_id_list)
        customers_serializer = CustomerSerializer(customers, many=True)
        return Response(customers_serializer.data, status=status.HTTP_200_OK)


class SaveCreditClearanceViewSet(viewsets.ModelViewSet):
    permission_classes = [CreditManagementPermission]
    queryset = CreditClearance.objects.all().select_related("sale_master", "ref_credit_clearance")
    serializer_class = SaveCreditClearanceSerializer
    http_method_names = ['post']

    @transaction.atomic
    def create(self, request):
        return super(SaveCreditClearanceViewSet, self).create(request)
