from datetime import timedelta
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
from src.sale.models import SaleMaster
from ..dashboard_permissions import AllDashBoardPermission
from ..serializers import SaleChartSerializer


def get_week_sale(query, after, before):
    if query == 'count':
        return SaleMaster.objects.filter(
            sale_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            sale_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return SaleMaster.objects.filter(
            sale_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            sale_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


def get_week_sale_return(query, after, before):
    if query == 'count':
        return SaleMaster.objects.filter(
            sale_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            sale_return_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return SaleMaster.objects.filter(
            sale_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            sale_return_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


class SalesVsSalesReturnListAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    serializer_class = SaleChartSerializer

    def get_queryset(self):
        data = {
            "date": [],
            "sale_amount": [],
            "sale_return_amount": [],
        }
        current_fiscal_year = int(get_full_fiscal_year_code_bs().split('/')[0])
        start_date_bs = nepali_datetime.date(current_fiscal_year, 4, 1)

        start_date_ad = start_date_bs.to_datetime_date()
        current_date_ad = timezone.now().date().replace(day=1)

        sales = SaleMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                          created_date_ad__lte=timezone.now(),
                                          sale_type=1).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            sale_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'sale_amount').order_by('date')

        sale_returns = SaleMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                                 created_date_ad__lte=timezone.now(),
                                                 sale_type=2).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            sale_return_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'sale_return_amount').order_by('date')

        while current_date_ad >= start_date_ad:
            month = current_date_ad.month
            sale_data = 0.00
            sale_return_data = 0.00

            sale_amount = sales.filter(date=current_date_ad.month).values_list('sale_amount', flat=True)
            if sale_amount:
                sale_data = sale_amount[0]

            sale_return_amount = sale_returns.filter(date=current_date_ad.month).values_list(
                'sale_return_amount', flat=True)
            if sale_return_amount:
                sale_return_data = sale_return_amount[0]

            data['date'].append(month)
            data['sale_amount'].append(sale_data)
            data['sale_return_amount'].append(sale_return_data)

            current_date_ad -= relativedelta(months=1)

        data['date'].reverse()
        data['sale_amount'].reverse()
        data['sale_return_amount'].reverse()
        return data

    def get(self, request, *args, **kwargs):
        current_date_before = timezone.now().date()
        current_date_after = timezone.now().date() - timedelta(days=7)
        last_week_date_before = current_date_after
        last_week_date_after = current_date_after - timedelta(days=7)

        last_week = {}
        current_week = {}

        # last week sale
        last_week.update(get_week_sale('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_sale('cost', last_week_date_after, last_week_date_before))

        # last week sale return
        last_week.update(get_week_sale_return('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_sale_return('cost', last_week_date_after, last_week_date_before))

        # current week sale
        current_week.update(get_week_sale('count', current_date_after, current_date_before))
        current_week.update(get_week_sale('cost', current_date_after, current_date_before))

        # current week sale cost
        current_week.update(get_week_sale_return('count', current_date_after, current_date_before))
        current_week.update(get_week_sale_return('cost', current_date_after, current_date_before))

        return Response({
            "last_week": last_week,
            "current_week": current_week,
            "sale_chart": self.get_queryset()
        }, status=status.HTTP_200_OK)
