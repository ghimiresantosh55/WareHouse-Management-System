from datetime import timedelta
from decimal import Decimal

import nepali_datetime
from dateutil.relativedelta import relativedelta
from django.db.models import DecimalField, Sum, Count
from django.db.models.functions import Coalesce, ExtractMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.custom_lib.functions.fiscal_year import get_full_fiscal_year_code_bs
from ..dashboard_permissions import AllDashBoardPermission
from ..serializers import CreditChartSerializer
from ...credit_management.models import CreditClearance
from ...sale.models import SaleMaster


def get_week_sale_credit(query, after, before):
    if query == 'count':
        return SaleMaster.objects.filter(
            sale_type=1,
            pay_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            credit_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return SaleMaster.objects.filter(
            sale_type=1,
            pay_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            credit_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


def get_week_credit_clearance(query, after, before):
    if query == 'count':
        return CreditClearance.objects.filter(
            payment_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            credit_clearance_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return CreditClearance.objects.filter(
            payment_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            credit_clearance_cost=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal("0.00"))
        )


class CreditVsCreditClearanceChartAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    serializer_class = CreditChartSerializer

    def get_queryset(self):
        data = {
            "date": [],
            "credit_amount": [],
            "credit_clearance_amount": [],
        }
        current_fiscal_year = int(get_full_fiscal_year_code_bs().split('/')[0])
        start_date_bs = nepali_datetime.date(current_fiscal_year, 4, 1)

        start_date_ad = start_date_bs.to_datetime_date()
        current_date_ad = timezone.now().date().replace(day=1)

        sale_credits = SaleMaster.objects.filter(sale_type=1,
                                                 pay_type=2,
                                                 created_date_ad__gte=start_date_ad,
                                                 created_date_ad__lte=timezone.now(),
                                                 ).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            credit_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'credit_amount').order_by('date')

        credit_clearances = CreditClearance.objects.filter(payment_type=1,
                                                           created_date_ad__gte=start_date_ad,
                                                           created_date_ad__lte=timezone.now(),
                                                           ).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            credit_clearance_amount=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'credit_clearance_amount').order_by('date')

        while current_date_ad >= start_date_ad:
            month = current_date_ad.month
            credit_data = 0.00
            credit_clearance_data = 0.00

            credit_amount = sale_credits.filter(date=current_date_ad.month).values_list('credit_amount', flat=True)
            if credit_amount:
                credit_data = credit_amount[0]

            credit_clearance_amount = credit_clearances.filter(date=current_date_ad.month).values_list(
                'credit_clearance_amount', flat=True)
            if credit_clearance_amount:
                credit_clearance_data = credit_clearance_amount[0]

            data['date'].append(month)
            data['credit_amount'].append(credit_data)
            data['credit_clearance_amount'].append(credit_clearance_data)

            current_date_ad -= relativedelta(months=1)

        data['date'].reverse()
        data['credit_amount'].reverse()
        data['credit_clearance_amount'].reverse()
        return data

    def get(self, request, *args, **kwargs):
        current_date_before = timezone.now().date()
        current_date_after = timezone.now().date() - timedelta(days=7)
        last_week_date_before = current_date_after
        last_week_date_after = current_date_after - timedelta(days=7)

        last_week = {}
        current_week = {}

        # last week credit
        last_week.update(get_week_sale_credit('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_sale_credit('cost', last_week_date_after, last_week_date_before))

        # last week party payment
        last_week.update(get_week_credit_clearance('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_credit_clearance('cost', last_week_date_after, last_week_date_before))

        # current week credit
        current_week.update(get_week_sale_credit('count', current_date_after, current_date_before))
        current_week.update(get_week_sale_credit('cost', current_date_after, current_date_before))

        # current week party payment
        current_week.update(get_week_credit_clearance('count', current_date_after, current_date_before))
        current_week.update(get_week_credit_clearance('cost', current_date_after, current_date_before))

        return Response({
            "last_week": last_week,
            "current_week": current_week,
            "credit_chart": self.get_queryset()
        }, status=status.HTTP_200_OK)
