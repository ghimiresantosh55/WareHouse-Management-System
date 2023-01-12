from django.db.models import Q, F
from django.db.models import Sum
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from src.customer_order.models import OrderMaster
from ..fixes.error_fixes import fix_customer_order_total_amounts


class CustomerOrderTotalAmountCalcView(ListAPIView):

    def get_queryset(self):
        queryset = OrderMaster.objects.exclude(status=3).values('id', 'sub_total', 'grand_total', 'order_no').annotate(
            total_gross_amount=Sum('order_details__gross_amount', filter=Q(order_details__cancelled=False)),
            total_net_amount=Sum('order_details__net_amount', filter=Q(order_details__cancelled=False)),
        ).exclude(Q(sub_total=F('total_gross_amount')) & Q(grand_total=F('total_net_amount')))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class FixTotalAmountsCustomerOrderApiView(APIView):
    def get(self, request):
        fix_customer_order_total_amounts()
        return Response({'message': 'amounts fixed for customer order'})
