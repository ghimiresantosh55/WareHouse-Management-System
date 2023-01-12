from decimal import Decimal

from django.db.models import Case, When, Value, CharField, DecimalField, Q
from django.db.models import F
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.financial_report.serializer.party_report_serializers import SupplierAndCustomerReportSerializer
from src.purchase.models import PurchaseMaster
from src.sale.models import SaleMaster


class SupplierAndCustomerReportApiView(ListAPIView):
    serializer_class = SupplierAndCustomerReportSerializer

    def get_queryset(self):
        query_params = {}
        if self.request.GET.get('date_after'):
            query_params['date_after'] = self.request.GET.get('date_after')

        if self.request.GET.get('date_before'):
            query_params['date_before'] = self.request.GET.get('date_before')

        purchase = PurchaseMaster.objects.filter(purchase_type__in=[1, 2]).annotate(
            party_name=F('supplier__name'),
            operation_type=Case(
                When(purchase_type=1, then=Value('PURCHASE')),
                When(purchase_type=2, then=Value('PURCHASE-RETURN')),
                default=Value('N/A'),
                output_field=CharField()),
            debit=Case(
                When(purchase_type=1, then=F('grand_total'), ),
                When(purchase_type=2, then=Value("0.00"), ),
                output_field=DecimalField()
            ),
            credit=Case(
                When(Q(purchase_type=1) & Q(pay_type=1), then=F('grand_total')),
                When(Q(purchase_type=1) & Q(pay_type=2), then=Decimal("0.00"), ),
                When(Q(purchase_type=2), then=F('grand_total'), ),

                default=Decimal("0.00")
            ),
        ).values('id', 'party_name', 'operation_type', 'debit', 'credit', 'created_date_ad').order_by(
            "-created_date_ad")

        sale = SaleMaster.objects.annotate(
            party_name=F('customer__first_name'),
            operation_type=Case(
                When(sale_type=1, then=Value('SALE')),
                When(sale_type=2, then=Value('SALE-RETURN')),
                default=Value('N/A'),
                output_field=CharField()),
            debit=Case(
                When(Q(sale_type=1) & Q(pay_type=1), then=F('grand_total')),
                When(Q(sale_type=1) & Q(pay_type=2), then=Decimal("0.00"), ),
                When(Q(sale_type=2), then=F('grand_total'), ),
                default=Decimal("0.00")
            ),
            credit=Case(
                When(Q(sale_type=1) & Q(pay_type=1), then=F('grand_total')),
                When(Q(sale_type=1) & Q(pay_type=2), then=F('grand_total'), ),
                When(Q(sale_type=1) & Q(pay_type=1), then=F('grand_total'), ),
                When(Q(sale_type=1) & Q(pay_type=2), then=Decimal("0.00"), ),
                default=Decimal("0.00")
            ),
        ).values('id', 'party_name', 'operation_type', 'debit', 'credit', 'created_date_ad').order_by(
            "-created_date_ad")
        queryset = purchase.union(sale).order_by("-created_date_ad")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
