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
from ..serializers import PartyPaymentChartSerializer

from src.custom_lib.functions.fiscal_year import get_full_fiscal_year_code_bs
from ..dashboard_permissions import AllDashBoardPermission
from ..serializers import CreditChartSerializer
from ...party_payment.models import PartyPayment
from ...purchase.models import PurchaseMaster


def get_week_party_payment(query, after, before):
    if query == 'count':
        return PurchaseMaster.objects.filter(
            purchase_type=1,
            pay_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            party_payment_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return PurchaseMaster.objects.filter(
            purchase_type=1,
            pay_type=2,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            party_payment_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )


def get_week_party_payment_clearance(query, after, before):
    if query == 'count':
        return PartyPayment.objects.filter(
            payment_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before,
        ).distinct().aggregate(
            party_payment_clearance_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )
    else:
        return PartyPayment.objects.filter(
            payment_type=1,
            created_date_ad__date__gte=after,
            created_date_ad__date__lte=before).distinct().aggregate(
            party_payment_clearance_cost=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal("0.00"))
        )


class PartyPaymentVsPartyPaymentClearanceListAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    serializer_class = PartyPaymentChartSerializer

    def get_queryset(self):
        data = {
            "date": [],
            "party_payment_amount": [],
            "party_payment_clearance_amount": [],
        }
        current_fiscal_year = int(get_full_fiscal_year_code_bs().split('/')[0])
        start_date_bs = nepali_datetime.date(current_fiscal_year, 4, 1)

        start_date_ad = start_date_bs.to_datetime_date()
        current_date_ad = timezone.now().date().replace(day=1)

        party_payments = PurchaseMaster.objects.filter(purchase_type=1,
                                                       pay_type=2,
                                                       created_date_ad__gte=start_date_ad,
                                                       created_date_ad__lte=timezone.now(),
                                                       ).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            party_payment_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'party_payment_amount').order_by('date')

        party_payment_clearances = PartyPayment.objects.filter(payment_type=1,
                                                               created_date_ad__gte=start_date_ad,
                                                               created_date_ad__lte=timezone.now(),
                                                               ).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            party_payment_clearance_amount=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'party_payment_clearance_amount').order_by('date')

        while current_date_ad >= start_date_ad:
            month = current_date_ad.month
            party_payment_data = 0.00
            party_payment_clearance_data = 0.00

            party_payment_amount = party_payments.filter(date=current_date_ad.month).values_list('party_payment_amount', flat=True)
            if party_payment_amount:
                party_payment_data = party_payment_amount[0]

            party_payment_clearance_amount = party_payment_clearances.filter(date=current_date_ad.month).values_list(
                'party_payment_clearance_amount', flat=True)
            if party_payment_clearance_amount:
                party_payment_clearance_data = party_payment_clearance_amount[0]

            data['date'].append(month)
            data['party_payment_amount'].append(party_payment_data)
            data['party_payment_clearance_amount'].append(party_payment_clearance_data)

            current_date_ad -= relativedelta(months=1)

        data['date'].reverse()
        data['party_payment_amount'].reverse()
        data['party_payment_clearance_amount'].reverse()
        return data

    def get(self, request, *args, **kwargs):
        current_date_before = timezone.now().date()
        current_date_after = timezone.now().date() - timedelta(days=7)
        last_week_date_before = current_date_after
        last_week_date_after = current_date_after - timedelta(days=7)

        last_week = {}
        current_week = {}

        # last week credit
        last_week.update(get_week_party_payment('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_party_payment('cost', last_week_date_after, last_week_date_before))

        # last week party payment
        last_week.update(get_week_party_payment_clearance('count', last_week_date_after, last_week_date_before))
        last_week.update(get_week_party_payment_clearance('cost', last_week_date_after, last_week_date_before))

        # current week credit
        current_week.update(get_week_party_payment('count', current_date_after, current_date_before))
        current_week.update(get_week_party_payment('cost', current_date_after, current_date_before))

        # current week party payment
        current_week.update(get_week_party_payment_clearance('count', current_date_after, current_date_before))
        current_week.update(get_week_party_payment_clearance('cost', current_date_after, current_date_before))

        return Response({
            "last_week": last_week,
            "current_week": current_week,
            "payment_chart": self.get_queryset()
        }, status=status.HTTP_200_OK)
