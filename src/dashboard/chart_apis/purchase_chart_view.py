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
from src.purchase.models import PurchaseMaster
from ..dashboard_permissions import AllDashBoardPermission
from ..serializers import PurchaseChartSerializer


def get_week_purchase(query, after, before):
    if query == 'count':
        return PurchaseMaster.objects.filter(
            purchase_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            purchase_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return PurchaseMaster.objects.filter(
            purchase_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            purchase_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


def get_week_purchase_return(query, after, before):
    if query == 'count':
        return PurchaseMaster.objects.filter(
            purchase_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            purchase_return_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return PurchaseMaster.objects.filter(
            purchase_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            purchase_return_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


class PurchaseVsPurchaseReturnListAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    serializer_class = PurchaseChartSerializer

    def get_queryset(self):
        data = {
            "date": [],
            "purchase_amount": [],
            "purchase_return_amount": [],
        }
        current_fiscal_year = int(get_full_fiscal_year_code_bs().split('/')[0])
        start_date_bs = nepali_datetime.date(current_fiscal_year, 4, 1)

        start_date_ad = start_date_bs.to_datetime_date()
        current_date_ad = timezone.now().date().replace(day=1)

        purchases = PurchaseMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                                  created_date_ad__lte=timezone.now(),
                                                  purchase_type=1).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            purchase_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'purchase_amount').order_by('date')

        purchase_returns = PurchaseMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                                         created_date_ad__lte=timezone.now(),
                                                         purchase_type=2).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            purchase_return_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'purchase_return_amount').order_by('date')

        while current_date_ad >= start_date_ad:
            month = current_date_ad.month
            purchase_data = 0.00
            purchase_return_data = 0.00

            purchase_amount = purchases.filter(date=current_date_ad.month).values_list('purchase_amount', flat=True)
            if purchase_amount:
                purchase_data = purchase_amount[0]

            purchase_return_amount = purchase_returns.filter(date=current_date_ad.month).values_list(
                'purchase_return_amount', flat=True)
            if purchase_return_amount:
                purchase_return_data = purchase_return_amount[0]

            data['date'].append(month)
            data['purchase_amount'].append(purchase_data)
            data['purchase_return_amount'].append(purchase_return_data)

            current_date_ad -= relativedelta(months=1)

        data['date'].reverse()
        data['purchase_amount'].reverse()
        data['purchase_return_amount'].reverse()
        return data

        # data = []
        # current_fiscal_year = get_full_fiscal_year_code_ad()
        # year_start = current_fiscal_year[:4]
        # year_end = int(year_start) + 1
        # purchases = PurchaseMaster.objects.filter(created_date_ad__year__gte=year_start,
        #                                           created_date_ad__year__lte=year_end,
        #                                           purchase_type=1).annotate(
        #     date=ExtractMonth('created_date_ad'),
        # ).values('date').annotate(
        #     purchase_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")
        # )).values('date', 'purchase_amount')
        #
        # purchase_returns = PurchaseMaster.objects.filter(created_date_ad__year__gte=year_start,
        #                                                  created_date_ad__year__lte=year_end,
        #                                                  purchase_type=2).annotate(
        #     date=ExtractMonth('created_date_ad')
        # ).values('date').annotate(
        #     purchase_return_amount=Coalesce(
        #         Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        # ).values('date', 'purchase_return_amount')
        #
        # if not purchase_returns:
        #     for i in purchases:
        #         data.append({
        #             **i,
        #             "purchase_return_amount": Decimal("0.00")
        #         })
        # elif not purchases:
        #     for purchase_return in purchase_returns:
        #         data.append({
        #             "purchase_amount": Decimal("0.00"),
        #             **purchase_return
        #         })
        # else:
        #     result = zip(purchases, purchase_returns)
        #     for p, pr in result:
        #         data.append({
        #             **p, **pr
        #         })
        #
        # return sorted(data, key=operator.itemgetter('date'))

    def get(self, request, *args, **kwargs):
        current_date_before = timezone.now().date()
        current_date_after = timezone.now().date() - timedelta(days=7)
        last_week_date_before = current_date_after
        last_week_date_after = current_date_after - timedelta(days=7)

        last_week = {}
        current_week = {}

        # last week purchase
        last_week.update(get_week_purchase('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_purchase('cost', last_week_date_after, last_week_date_before))

        # last week purchase return
        last_week.update(get_week_purchase_return('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_purchase_return('cost', last_week_date_after, last_week_date_before))

        # current week purchase
        current_week.update(get_week_purchase('count', current_date_after, current_date_before))
        current_week.update(get_week_purchase('cost', current_date_after, current_date_before))

        # current week purchase cost
        current_week.update(get_week_purchase_return('count', current_date_after, current_date_before))
        current_week.update(get_week_purchase_return('cost', current_date_after, current_date_before))

        return Response({
            "last_week": last_week,
            "current_week": current_week,
            "purchase_chart": self.get_queryset()
        }, status=status.HTTP_200_OK)
