from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.chalan.models import ChalanMaster
from src.customer_order.models import OrderMaster
from src.dashboard.dashboard_permissions import AllDashBoardPermission
from src.purchase.models import PurchaseOrderMaster
from src.sale.models import SaleMaster


class LastAndCurrentWeekStaticalDashboardAPIView(APIView):
    permission_classes = [AllDashBoardPermission]

    def get(self, request, *args, **kwargs):

        current_date_before = timezone.now().date()
        current_date_after = timezone.now().date() - timedelta(days=7)

        last_week_date_before = current_date_after
        last_week_date_after = current_date_after - timedelta(days=7)

        last_week = {}
        current_week = {}

        last_week_order_count = OrderMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before
        ).distinct().aggregate(
            order_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        last_week_order_cost = OrderMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before).distinct().aggregate(
            order_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )

        current_week_order_count = OrderMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before
        ).distinct().aggregate(
            order_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        current_week_order_cost = OrderMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before).distinct().aggregate(
            order_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )

        last_week.update(last_week_order_count)
        last_week.update(last_week_order_cost)
        current_week.update(current_week_order_count)
        current_week.update(current_week_order_cost)

        last_week_purchase_order_count = PurchaseOrderMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before
        ).distinct().aggregate(
            purchase_order_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        last_week_purchase_order_cost = PurchaseOrderMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before).distinct().aggregate(
            purchase_order_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )
        current_week_purchase_order_count = PurchaseOrderMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before
        ).distinct().aggregate(
            purchase_order_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        current_week_purchase_order_cost = PurchaseOrderMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before).distinct().values().aggregate(
            purchase_order_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )

        last_week.update(last_week_purchase_order_count)
        last_week.update(last_week_purchase_order_cost)
        current_week.update(current_week_purchase_order_count)
        current_week.update(current_week_purchase_order_cost)

        last_week_sales_count = SaleMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before
        ).distinct().aggregate(
            sales_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        last_week_sales_cost = SaleMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before).distinct().aggregate(
            sales_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )

        current_week_sales_count = SaleMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before
        ).distinct().aggregate(
            sales_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        current_week_sales_cost = SaleMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before).distinct().aggregate(
            sales_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )

        last_week.update(last_week_sales_count)
        last_week.update(last_week_sales_cost)
        current_week.update(current_week_sales_count)
        current_week.update(current_week_sales_cost)

        last_week_chalan_count = ChalanMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before
        ).distinct().aggregate(
            chalan_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        last_week_chalan_cost = ChalanMaster.objects.filter(
            created_date_ad__date__gte=last_week_date_after,
            created_date_ad__date__lte=last_week_date_before).distinct().aggregate(
            chalan_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )

        current_week_chalan_count = ChalanMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before
        ).distinct().aggregate(
            chalan_count=Coalesce(Count("id", output_field=DecimalField()), Decimal("0.00"))
        )

        current_week_chalan_cost = ChalanMaster.objects.filter(
            created_date_ad__date__gte=current_date_after,
            created_date_ad__date__lte=current_date_before).distinct().aggregate(
            chalan_cost=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        )

        last_week.update(last_week_chalan_count)
        last_week.update(last_week_chalan_cost)
        current_week.update(current_week_chalan_count)
        current_week.update(current_week_chalan_cost)

        return Response({
            "last_week": last_week,
            "current_week": current_week
        },
            status=status.HTTP_200_OK)
