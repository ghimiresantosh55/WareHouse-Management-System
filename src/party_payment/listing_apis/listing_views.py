from decimal import Decimal

from django.db.models import Sum, Q, DecimalField, OuterRef, Subquery, F
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.core_app.models import PaymentMode
from src.supplier.models import Supplier
from .listing_serializers import SupplierPartyPaymentListSerializer, PaymentModePartyPaymentListSerializer
from ..models import PartyPayment
from ..party_payment_permissions import PartyPaymentPermission
from ...purchase.models import PurchaseMaster


class SupplierListView(ListAPIView):
    # queryset = Supplier.objects.filter(active=True)
    permission_classes = [PartyPaymentPermission]
    serializer_class = SupplierPartyPaymentListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id']
    search_fields = ['name', 'pan_vat_no', 'phone_no']
    filter_fields = ['id', 'phone_no']

    def get_queryset(self):
        total_amount = PurchaseMaster.objects.filter(
            supplier=OuterRef('pk'), pay_type=2, purchase_type=1).values('supplier').annotate(
            total_amount=Sum('grand_total')).values('total_amount')
        returned_amount = PurchaseMaster.objects.filter(
            supplier=OuterRef('pk'), purchase_type=2, pay_type=2).values('supplier').annotate(
            returned_amount=Sum('grand_total')).values('returned_amount')
        paid_amount = PartyPayment.objects.filter(
            purchase_master__supplier=OuterRef('pk'), payment_type=1).values('purchase_master__supplier').annotate(
            paid_amount=Sum('total_amount')).values('paid_amount')
        refund_amount = PartyPayment.objects.filter(
            purchase_master__supplier=OuterRef('pk'), payment_type=2).values('purchase_master__supplier').annotate(
            refund_amount=Sum('total_amount')).values('refund_amount')

        queryset = Supplier.objects.filter(active=True).annotate(
            created_by_user_name=F('created_by__user_name'),
            total_amount=Coalesce(
                Subquery(total_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            returned_amount=Coalesce(
                Subquery(returned_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            paid_amount=Coalesce(
                Subquery(paid_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            refund_amount=Coalesce(
                Subquery(refund_amount, output_field=DecimalField()), Decimal("0.00")
            )
        ).annotate(
            due_amount=(F('total_amount') - F('returned_amount')) - (F('paid_amount') - F('refund_amount'))
        ).filter(total_amount__gt=0).values(
            'id', 'name', 'pan_vat_no', 'paid_amount', 'refund_amount',
            'total_amount', 'returned_amount', 'due_amount', 'created_by_user_name'
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class PaymentModeListView(ListAPIView):
    queryset = PaymentMode.objects.filter(active=True)
    permission_classes = [PartyPaymentPermission]
    serializer_class = PaymentModePartyPaymentListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id']
    search_fields = ['name', 'remarks']
    filter_fields = ['id']
