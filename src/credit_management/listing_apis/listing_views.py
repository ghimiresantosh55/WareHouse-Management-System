from decimal import Decimal

from django.db.models import Sum, DecimalField, OuterRef, Subquery, F
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.core_app.models import PaymentMode
from src.credit_management.models import CreditClearance
from src.customer.models import Customer
from src.sale.models import SaleMaster
from .listing_serializers import CustomerCreditClearanceListSerializer, PaymentModeCreditClearanceSerializer
from ..credit_management_permissions import CreditManagementPermission


class CustomerListView(ListAPIView):
    queryset = Customer.objects.filter(active=True)
    permission_classes = [CreditManagementPermission]
    serializer_class = CustomerCreditClearanceListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id']
    search_fields = ['first_name', 'pan_vat_no', 'phone_no']
    filter_fields = ['id', 'phone_no']

    def get_queryset(self):
        credit_amount = SaleMaster.objects.filter(
            customer=OuterRef("pk"), pay_type=2, ref_sale_master__isnull=True).values('customer').annotate(
            total_amount=Sum('grand_total')).values('total_amount')

        credit_return_amount = SaleMaster.objects.filter(
            customer=OuterRef("pk"), sale_type=2, pay_type=2).values('customer').annotate(
            returned_amount=Sum('grand_total')).values('returned_amount')

        paid_amount = CreditClearance.objects.filter(
            sale_master__customer=OuterRef("pk"), payment_type=1).values('sale_master__customer').annotate(
            paid_amount=Sum('total_amount')).values('paid_amount')

        refund_amount = CreditClearance.objects.filter(
            sale_master__customer=OuterRef("pk"), payment_type=2).values('sale_master__customer').annotate(
            refund_amount=Sum('total_amount')).values('refund_amount')

        customer_data = Customer.objects.annotate(
            credit_amount=Coalesce(Subquery(credit_amount, output_field=DecimalField()), Decimal("0.00")) -
                          Coalesce(Subquery(credit_return_amount,
                                            output_field=DecimalField()), Decimal("0.00")),
            paid_amount=Coalesce(Subquery(paid_amount, output_field=DecimalField()), Decimal("0.00")) -
                        Coalesce(Subquery(refund_amount,
                                          output_field=DecimalField()), Decimal("0.00")),
        ).annotate(
            due_amount=F('credit_amount') - F('paid_amount')
        ).filter(credit_amount__gt=0).values('id', 'first_name', 'middle_name', 'last_name', 'credit_amount',
                                             'paid_amount', 'pan_vat_no',
                                             'phone_no', 'due_amount')

        return customer_data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class PaymentModeListView(ListAPIView):
    queryset = PaymentMode.objects.filter(active=True)
    permission_classes = [CreditManagementPermission]
    serializer_class = PaymentModeCreditClearanceSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id']
    search_fields = ['name', 'remarks']
    filter_fields = ['id']
