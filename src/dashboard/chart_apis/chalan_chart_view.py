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

from src.chalan.models import ChalanMaster
from src.custom_lib.functions.fiscal_year import get_full_fiscal_year_code_bs
from ..dashboard_permissions import AllDashBoardPermission
from ..serializers import ChalanChartSerializer


def get_week_chalan(query, after, before):
    if query == 'count':
        return ChalanMaster.objects.filter(
            status=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            chalan_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return ChalanMaster.objects.filter(
            status=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            chalan_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


def get_week_chalan_return(query, after, before):
    if query == 'count':
        return ChalanMaster.objects.filter(
            status=3,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            chalan_return_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return ChalanMaster.objects.filter(
            status=3,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            chalan_return_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


class ChalanVsChalanReturnListAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    serializer_class = ChalanChartSerializer

    def get_queryset(self):
        data = {
            "date": [],
            "chalan_amount": [],
            "chalan_return_amount": [],
        }
        current_fiscal_year = int(get_full_fiscal_year_code_bs().split('/')[0])
        start_date_bs = nepali_datetime.date(current_fiscal_year, 4, 1)

        start_date_ad = start_date_bs.to_datetime_date()
        current_date_ad = timezone.now().date().replace(day=1)

        chalans = ChalanMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                                  created_date_ad__lte=timezone.now(),
                                                  status=1).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            chalan_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'chalan_amount').order_by('date')

        chalan_returns = ChalanMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                                         created_date_ad__lte=timezone.now(),
                                                         status=3).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            chalan_return_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'chalan_return_amount').order_by('date')

        while current_date_ad >= start_date_ad:
            month = current_date_ad.month
            chalan_data = 0.00
            chalan_return_data = 0.00

            chalan_amount = chalans.filter(date=current_date_ad.month).values_list('chalan_amount', flat=True)
            if chalan_amount:
                chalan_data = chalan_amount[0]

            chalan_return_amount = chalan_returns.filter(date=current_date_ad.month).values_list(
                'chalan_return_amount', flat=True)
            if chalan_return_amount:
                chalan_return_data = chalan_return_amount[0]

            data['date'].append(month)
            data['chalan_amount'].append(chalan_data)
            data['chalan_return_amount'].append(chalan_return_data)

            current_date_ad -= relativedelta(months=1)

        data['date'].reverse()
        data['chalan_amount'].reverse()
        data['chalan_return_amount'].reverse()
        return data

    def get(self, request, *args, **kwargs):
        current_date_before = timezone.now().date()
        current_date_after = timezone.now().date() - timedelta(days=7)
        last_week_date_before = current_date_after
        last_week_date_after = current_date_after - timedelta(days=7)

        last_week = {}
        current_week = {}

        # last week chalan
        last_week.update(get_week_chalan('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_chalan('cost', last_week_date_after, last_week_date_before))

        # last week chalan return
        last_week.update(get_week_chalan_return('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_chalan_return('cost', last_week_date_after, last_week_date_before))

        # current week chalan
        current_week.update(get_week_chalan('count', current_date_after, current_date_before))
        current_week.update(get_week_chalan('cost', current_date_after, current_date_before))

        # current week chalan cost
        current_week.update(get_week_chalan_return('count', current_date_after, current_date_before))
        current_week.update(get_week_chalan_return('cost', current_date_after, current_date_before))

        return Response({
            "last_week": last_week,
            "current_week": current_week,
            "chalan_chart": self.get_queryset()
        }, status=status.HTTP_200_OK)
