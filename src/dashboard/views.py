from decimal import Decimal

import nepali_datetime
from dateutil.relativedelta import relativedelta
from django.db import connection
from django.db.models import Q, IntegerField
from django.db.models import Sum
from django.db.models import fields, DecimalField, OuterRef, Subquery, F
from django.db.models.aggregates import Count
from django.db.models.functions import Coalesce
from django.db.models.functions import ExtractMonth
from django.db.models.functions.comparison import Cast
from django.utils import timezone
from django_filters import FilterSet, DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
# Create your views here.
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from src.credit_management.models import CreditClearance
from src.credit_management.serializers import CreditPaymentMasterSerializer
from src.customer_order.models import OrderMaster
from src.customer_order.serializers import OrderSummaryCustomerSerializer
from src.item.models import Item
from src.item.serializers import ItemSerializer
from src.purchase.models import PurchaseMaster, PurchaseOrderMaster
from src.purchase.serializers import PurchaseMasterSerializer
from src.sale.models import SaleMaster, SaleDetail
from src.sale.serializers import SaleMasterSerializer
from .dashboard_permissions import AllDashBoardPermission
from .serializers import TopCustomerListSerializer, TopSupplierListSerializer, TopItemListSerializer
from ..chalan.models import ChalanDetail
from ..custom_lib.functions.fiscal_year import get_full_fiscal_year_code_bs
from ..customer.models import Customer
from ..supplier.models import Supplier

'''---------------------------------- Financial Dashboard ---------------------------------'''


class FinancialDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllDashBoardPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = PurchaseMasterSerializer

    def list(self, request, *args, **kwargs):
        query_dict = {

        }
        for k, vals in request.GET.lists():

            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        # query_dict['filter-class']=FilterForPurchase
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        # purchase data
        data = {}
        purchase_amount_data = PurchaseMaster.objects.filter(purchase_type=1, **query_filter).aggregate(
            total_purchase_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        purchase_return_data = PurchaseMaster.objects.filter(purchase_type=2, **query_filter) \
            .aggregate(
            total_purchase_return_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        data.update(purchase_amount_data)
        data.update(purchase_return_data)

        # Sale Data
        sale_amount_data = SaleMaster.objects.filter(sale_type=1, **query_filter) \
            .aggregate(total_sale_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        sale_return_data = SaleMaster.objects.filter(sale_type=2, **query_filter) \
            .aggregate(
            total_sale_return_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        data.update(sale_amount_data)
        data.update(sale_return_data)

        # Credit Sale Data
        credit_sale_data = SaleMaster.objects.filter(pay_type=2, **query_filter) \
            .aggregate(credit_sale_total=Coalesce(Sum('grand_total'), Decimal("0.00")))
        credit_payment_data = CreditClearance.objects.filter(**query_filter) \
            .aggregate(credit_collection_total=Coalesce(Sum('total_amount'), Decimal("0.00")))

        data.update(credit_sale_data)
        data.update(credit_payment_data)

        return Response(data, status=status.HTTP_200_OK)


class GetPurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllDashBoardPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = PurchaseMasterSerializer

    def list(self, request, *args, **kwargs):
        query_dict = {

        }
        for k, vals in request.GET.lists():

            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        # query_dict['filter-class']=FilterForPurchase
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']
        summary_data = {}
        data = {}
        # purchase_summary
        purchase_amount_data = PurchaseMaster.objects.filter(purchase_type=1, **query_filter) \
            .aggregate(total_purchase_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        purchase_return_data = PurchaseMaster.objects.filter(purchase_type=2, **query_filter) \
            .aggregate(
            total_purchase_return_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        summary_data.update(purchase_amount_data)
        summary_data.update(purchase_return_data)

        purchase_data = PurchaseMaster.objects.filter(**query_filter).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_purchase=Coalesce(Sum('grand_total', filter=Q(purchase_type=1), output_field=DecimalField()),
                                    Decimal("0.00")),
            total_purchase_return=Coalesce(Sum('grand_total', filter=Q(purchase_type=2), output_field=DecimalField()),
                                           Decimal("0.00"))) \
            .values('total_purchase', 'total_purchase_return', 'date_ad').order_by('date_ad')
        data['summary'] = summary_data
        data['data'] = purchase_data
        return Response(data, status=status.HTTP_200_OK)


class GetSaleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllDashBoardPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = SaleMasterSerializer

    def list(self, request, *args, **kwargs):
        query_dict = {

        }
        for k, vals in request.GET.lists():

            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']
        summary_data = {}
        data = {}
        # sale summary data
        sale_amount_data = SaleMaster.objects.filter(sale_type=1, **query_filter) \
            .aggregate(total_sale_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        sale_return_data = SaleMaster.objects.filter(sale_type=2, **query_filter) \
            .aggregate(
            total_sale_return_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))
        summary_data.update(sale_amount_data)
        summary_data.update(sale_return_data)
        sale_data = SaleMaster.objects.filter(**query_filter).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_sale=Coalesce(Sum('grand_total', filter=Q(sale_type=1), output_field=DecimalField()),
                                Decimal("0.00")),
            total_sale_return=Coalesce(Sum('grand_total', filter=Q(sale_type=2), output_field=DecimalField()),
                                       Decimal("0.00"))) \
            .values('date_ad', 'total_sale', 'total_sale_return').order_by('date_ad')
        data['summary'] = summary_data
        data['data'] = sale_data
        return Response(data, status=status.HTTP_200_OK)


class GetCreditSaleReportViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllDashBoardPermission]
    queryset = CreditClearance.objects.all()
    serializer_class = CreditPaymentMasterSerializer

    def list(self, request, *args, **kwargs):
        query_dict = {

        }
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}

        if query_dict:
            try:
                query_filter['created_date_ad__date__gte'] = query_dict['date_after']
                query_filter['created_date_ad__date__lte'] = query_dict['date_before']
            except KeyError:
                return Response("Please provide both date_after and date_before")
        summary_data = {}
        data = {}

        if query_filter:

            credit_sale_data = SaleMaster.objects.filter(pay_type=2, **query_filter) \
                .aggregate(credit_sale_total=Coalesce(Sum('grand_total'), 0))

            credit_payment_data = CreditClearance.objects.filter(payment_type=1, **query_filter) \
                .aggregate(credit_collection_total=Coalesce(Sum('total_amount'), 0))

            summary_data.update(credit_sale_data)
            summary_data.update(credit_payment_data)
            cursor = connection.cursor()
            cursor.execute('''select DATE(created_date_ad) created_date_ad, sum(credit_sale_amount) AS "credit_sale_amount", 
                                        sum (credit_coll) credit_clearance_amount from 
                                        (select DATE(created_date_ad) created_date_ad, sum(grand_total) credit_sale_amount, 0 as credit_coll from
                                                    sale_salemaster
                                        where sale_type = 1 and pay_type = 2 and DATE(created_date_ad)>= %s and DATE(created_date_ad)<= %s
                                        group by DATE(created_date_ad) 
                                        union all
                                        select DATE(created_date_ad) created_date_ad, 0 as credit_sale_amount, sum(total_amount) credit_coll from credit_management_creditclearance
                                        where payment_type = 1 and DATE(created_date_ad)>= %s and DATE(created_date_ad)<= %s
                                        group by DATE(created_date_ad)) R
                                        group by DATE(created_date_ad)''',
                           [query_filter["created_date_ad__date__gte"], query_filter["created_date_ad__date__lte"],
                            query_filter["created_date_ad__date__gte"], query_filter["created_date_ad__date__lte"]])
            columns = [col[0] for col in cursor.description]
            credit_data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            data['summary'] = summary_data
            data['data'] = credit_data
            return Response(data, status=status.HTTP_200_OK)


        else:
            credit_sale_data = SaleMaster.objects.filter(pay_type=2) \
                .aggregate(credit_sale_total=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00")))

            credit_payment_data = CreditClearance.objects.filter(payment_type=1) \
                .aggregate(
                credit_collection_total=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal("0.00")))

            summary_data.update(credit_sale_data)
            summary_data.update(credit_payment_data)
            cursor = connection.cursor()
            cursor.execute('''select DATE(created_date_ad) created_date_ad, sum(credit_sale_amount) AS "credit_sale_amount", 
                                            sum (credit_coll) credit_clearance_amount from 
                                            (select DATE(created_date_ad) created_date_ad, sum(grand_total) credit_sale_amount, 0 as credit_coll from
                                                        sale_salemaster
                                            where sale_type = 1 and pay_type = 2 
                                            group by DATE(created_date_ad) 
                                            union all
                                            select DATE(created_date_ad) created_date_ad, 0 as credit_sale_amount, sum(total_amount) credit_coll from credit_management_creditclearance
                                            where payment_type = 1 
                                            group by DATE(created_date_ad)) R
                                            group by DATE(created_date_ad)''')
            columns = [col[0] for col in cursor.description]
            credit_data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            data['summary'] = summary_data
            data['data'] = credit_data
        return Response(data, status=status.HTTP_200_OK)


''' ---------------------------------- Statistical Dashboard ---------------------------------------------------'''


class GetPurchaseCountViewSet(viewsets.ViewSet):
    permission_classes = [AllDashBoardPermission]
    serializer_class = PurchaseMaster
    queryset = PurchaseMaster.objects.all()

    def list(self, request, *args, **kwargs):
        query_dict = {}
        for k, vals in request.GET.lists():

            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        summary_data = {}
        data = {}
        # for summary data
        total_purchase_count_data = PurchaseMaster.objects.filter(**query_filter) \
            .aggregate(overall_total_purchase=Count("id"))
        total_purchase_return_data = PurchaseMaster.objects.filter(purchase_type=2, **query_filter) \
            .aggregate(overall_total_purchase_return=Count("id"))
        summary_data.update(total_purchase_count_data)
        summary_data.update(total_purchase_return_data)

        purchase_data = PurchaseMaster.objects.filter(**query_filter).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_purchase=Count("id"),
            total_purchase_return=Count("id", filter=Q(purchase_type=2))
        ).values('date_ad', 'total_purchase', 'total_purchase_return') \
            .order_by('created_date_ad__date')

        data['summary'] = summary_data
        data['data'] = purchase_data

        return Response(data, status=status.HTTP_200_OK)


class GetSaleCountViewSet(viewsets.ViewSet):
    permission_classes = [AllDashBoardPermission]
    serializers_class = SaleMasterSerializer
    queryset = SaleMaster.objects.all()

    def list(self, request, *args, **kwargs):
        query_dict = {}
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        summary_data = {}
        data = {}
        # for summary data
        total_sale_count_data = SaleMaster.objects.filter(**query_filter) \
            .aggregate(overall_total_sale=Count("id"))
        total_sale_return_data = SaleMaster.objects.filter(sale_type=2, **query_filter) \
            .aggregate(overall_total_sale_return=Count("id"))
        summary_data.update(total_sale_count_data)
        summary_data.update(total_sale_return_data)

        sale_count_data = SaleMaster.objects.filter(**query_filter).values('created_date_ad__date') \
            .annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_sale=Count("sale_no"),
            total_sale_return=Count("sale_no", filter=Q(sale_type=2))
        ).values("date_ad", "total_sale", "total_sale_return") \
            .order_by("date_ad")
        data["summary_data"] = summary_data
        data["data"] = sale_count_data
        return Response(data, status=status.HTTP_200_OK)


class GetCreditSaleCountViewSet(viewsets.ViewSet):
    permission_classes = [AllDashBoardPermission]
    serializers_class = SaleMasterSerializer
    queryset = SaleMaster.objects.all()

    def list(self, request, *args, **kwargs):
        query_dict = {}
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        summary_data = {}
        data = {}
        # for summary data
        total_sale_count_data = SaleMaster.objects.filter(**query_filter, pay_type=2) \
            .aggregate(overall_total_credit_sales=Count("id"))
        total_sale_return_data = SaleMaster.objects.filter(pay_type=2, **query_filter) \
            .aggregate(overall_total_credit_sale_return=Count("id", filter=Q(sale_type=2) & Q(pay_type=2)))
        summary_data.update(total_sale_count_data)
        summary_data.update(total_sale_return_data)

        credit_sale_data = SaleMaster.objects.filter(**query_filter, pay_type=2).values("created_date_ad__date") \
            .annotate(
            date_ad=Cast("created_date_ad", fields.DateField()),
            total_credit_sales=Count('sale_no'),
            total_credit_sale_return=Count('sale_no', filter=Q(sale_type=2) & Q(pay_type=2))
        ).values('date_ad', 'total_credit_sales', 'total_credit_sale_return') \
            .order_by('date_ad')
        data["summary_data"] = summary_data
        data["data"] = credit_sale_data
        return Response(data, status=status.HTTP_200_OK)


class GetActiveItemCountViewSet(viewsets.ViewSet):
    permission_classes = [AllDashBoardPermission]
    serializers_class = ItemSerializer
    queryset = Item.objects.all()

    def list(self, request, *args, **kwargs):
        query_dict = {}
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]

        data = Item.objects.filter(**query_dict) \
            .aggregate(
            total_items=Count('name'),
            total_active_items=Count('name', filter=Q(active=True)),
            total_deactivated_items=Count('name', filter=Q(active=False))
        )

        return Response(data, status=status.HTTP_200_OK)


class StaticalDashboardViewSet(viewsets.ViewSet):
    permission_classes = [AllDashBoardPermission]
    serializers_class = ItemSerializer
    queryset = Item.objects.all()

    def list(self, request, *args, **kwargs):
        query_dict = {}
        for k, vals in request.GET.lists():

            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]

        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']
        data = {}

        purchase_count = PurchaseMaster.objects.filter(**query_filter).values() \
            .aggregate(total_purchase=Count("id"))
        purchase_return = PurchaseMaster.objects.filter(**query_filter, purchase_type=2).values() \
            .aggregate(total_purchase_return=Count("id"))
        sale_count = SaleMaster.objects.filter(**query_filter).values() \
            .aggregate(total_sale=Count("id"))
        sale_return = SaleMaster.objects.filter(**query_filter, sale_type=2).values() \
            .aggregate(total_sale_return=Count("id"))
        credit_sale = SaleMaster.objects.filter(**query_filter, pay_type=2).values() \
            .aggregate(total_credit_sale=Count("id"))
        credit_sale_return = SaleMaster.objects.filter(Q(**query_filter) & Q(pay_type=2) & Q(sale_type=2)).values() \
            .aggregate(total_credit_sale_return=Count("id"))
        items = Item.objects.values() \
            .aggregate(total_items=Count("id"))
        active_items = Item.objects.filter(active=True).values() \
            .aggregate(total_active_items=Count("id"))
        customer_orders = OrderMaster.objects.filter(**query_filter).aggregate(total_customer_order=Count("id"))

        data.update(purchase_count)
        data.update(purchase_return)
        data.update(sale_count)
        data.update(sale_return)
        data.update(credit_sale)
        data.update(credit_sale_return)
        data.update(items)
        data.update(active_items)
        data.update(customer_orders)

        return Response(data, status=status.HTTP_200_OK)


class GetCustomerOrderCountViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllDashBoardPermission]
    queryset = OrderMaster.objects.all()
    serializer_class = OrderSummaryCustomerSerializer

    def list(self, request, *args, **kwargs):
        query_dict = {}
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date_gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        summary_data = {}
        data = {}

        total_customer_order_data = OrderMaster.objects.filter(**query_filter).aggregate(
            overall_total_customer_orders=Count("id")
        )
        total_customer_order_pending = OrderMaster.objects.filter(**query_filter, status=1).aggregate(
            overall_total_pending_customer_orders=Count("id")
        )
        total_customer_order_billed = OrderMaster.objects.filter(**query_filter, status=2).aggregate(
            overall_total_billed_customer_orders=Count("id")
        )
        total_customer_order_cancelled = OrderMaster.objects.filter(**query_filter, status=3).aggregate(
            overall_total_cancelled_customer_orders=Count("id")
        )
        total_customer_order_chalan = OrderMaster.objects.filter(**query_filter, status=4).aggregate(
            overall_total_chalan_customer_orders=Count("id")
        )
        total_customer_order_by_batch = OrderMaster.objects.filter(**query_filter, by_batch=True).aggregate(
            overall_total_customer_orders_by_batch=Count("id")
        )

        summary_data.update(total_customer_order_data)
        summary_data.update(total_customer_order_pending)
        summary_data.update(total_customer_order_billed)
        summary_data.update(total_customer_order_cancelled)
        summary_data.update(total_customer_order_chalan)
        summary_data.update(total_customer_order_by_batch)

        customer_order_data = OrderMaster.objects.filter(**query_filter).values("created_date_ad__date").annotate(
            date_ad=Cast('created_date_ad', fields.DateField()),
            total_orders=Count("id"),
            cancelled_orders=Count("id", filter=Q(status=3)),
            orders_billed=Count("id", filter=Q(status=2)),
            chalan_orders=Count("id", filter=Q(status=4)),
            by_batch_orders=Count("id", filter=Q(by_batch=True))
        ).values('date_ad', 'total_orders', 'orders_billed', 'cancelled_orders', 'chalan_orders', 'by_batch_orders')

        data['summary'] = summary_data
        data['data'] = customer_order_data

        return Response(data, status=status.HTTP_200_OK)


class FilterForCustomerOrderList(FilterSet):
    date = DateFromToRangeFilter(field_name="ordermaster__created_date_ad__date")

    class Meta:
        model = Customer
        fields = ['id', 'date']


class TopCustomersListAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    filter_class = FilterForCustomerOrderList
    queryset = Customer.objects.filter(active=True)
    serializer_class = TopCustomerListSerializer

    def get_queryset(self):

        queryset = self.queryset.filter(active=True)

        query_params = {}
        if self.request.GET.get('id'):
            queryset = queryset.filter(id=self.request.GET.get('id'))

        if self.request.GET.get('date_after'):
            query_params['date_after'] = self.request.GET.get('date_after')

        if self.request.GET.get('date_before'):
            query_params['date_before'] = self.request.GET.get('date_before')
        order_count = OrderMaster.objects.filter(customer=OuterRef("pk"),
                                                 created_date_ad__date__gte=query_params.get('date_after',
                                                                                             timezone.now().date()),
                                                 created_date_ad__date__lte=query_params.get('date_before',
                                                                                             timezone.now().date())
                                                 ).values('customer').annotate(
            order_count=Count('pk')
        ).values('order_count')

        queryset = queryset.annotate(
            order_count=Coalesce(Subquery(
                order_count, output_field=IntegerField()
            ), 0)
        ).values('id', 'first_name', 'middle_name', 'last_name', 'address', 'phone_no', 'order_count').order_by(
            '-order_count')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = queryset[:3]
        return Response(page, status=status.HTTP_200_OK)


class FilterForSupplierPurchaseList(FilterSet):
    date = DateFromToRangeFilter(field_name="purchasemaster__created_date_ad__date")

    class Meta:
        model = Supplier
        fields = ['id', 'date']


class TopSuppliersListAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    filter_class = FilterForSupplierPurchaseList
    queryset = Supplier.objects.filter(active=True)
    serializer_class = TopSupplierListSerializer

    def get_queryset(self):

        queryset = self.queryset.filter(active=True)

        query_params = {}
        if self.request.GET.get('id'):
            queryset = queryset.filter(id=self.request.GET.get('id'))

        if self.request.GET.get('date_after'):
            query_params['date_after'] = self.request.GET.get('date_after')

        if self.request.GET.get('date_before'):
            query_params['date_before'] = self.request.GET.get('date_before')
        purchase_order_count = PurchaseOrderMaster.objects.filter(supplier=OuterRef("pk"),
                                                                  created_date_ad__date__gte=query_params.get(
                                                                      'date_after',
                                                                      timezone.now().date()),
                                                                  created_date_ad__date__lte=query_params.get(
                                                                      'date_before',
                                                                      timezone.now().date())
                                                                  ).values('supplier').annotate(
            purchase_order_count=Count('pk')
        ).values('purchase_order_count')

        queryset = queryset.annotate(
            purchase_order_count=Coalesce(Subquery(
                purchase_order_count, output_field=IntegerField()
            ), 0)
        ).values('id', 'name', 'address', 'phone_no', 'purchase_order_count').order_by('-purchase_order_count')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = queryset[:3]
        return Response(page, status=status.HTTP_200_OK)


class FilterForItemSaleList(FilterSet):
    date = DateFromToRangeFilter(field_name="purchasemaster__created_date_ad__date")

    class Meta:
        model = Item
        fields = ['id', 'date']


class TopItemListAPIView(ListAPIView):
    permission_classes = [AllDashBoardPermission]
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    filter_class = FilterForItemSaleList
    queryset = Item.objects.filter(active=True)
    serializer_class = TopItemListSerializer

    def get_queryset(self):

        queryset = self.queryset.filter(active=True)

        query_params = {}
        if self.request.GET.get('id'):
            queryset = queryset.filter(id=self.request.GET.get('id'))

        if self.request.GET.get('date_after'):
            query_params['date_after'] = self.request.GET.get('date_after')

        if self.request.GET.get('date_before'):
            query_params['date_before'] = self.request.GET.get('date_before')
        item_sold_count_sale = SaleDetail.objects.filter(item=OuterRef("pk"),
                                                         created_date_ad__date__gte=query_params.get(
                                                             'date_after',
                                                             timezone.now().date()),
                                                         created_date_ad__date__lte=query_params.get(
                                                             'date_before',
                                                             timezone.now().date())
                                                         ).values('item').annotate(
            item_sold_count_sale=Count('pk')
        ).values('item_sold_count_sale')

        item_sold_count_chalan = ChalanDetail.objects.filter(item=OuterRef("pk"),
                                                             created_date_ad__date__gte=query_params.get(
                                                                 'date_after',
                                                                 timezone.now().date()),
                                                             created_date_ad__date__lte=query_params.get(
                                                                 'date_before',
                                                                 timezone.now().date())
                                                             ).values('item').annotate(
            item_sold_count_chalan=Count('pk')
        ).values('item_sold_count_chalan')

        queryset = queryset.annotate(
            item_sold_count_sale=Coalesce(Subquery(
                item_sold_count_sale, output_field=IntegerField()
            ), 0),
            item_sold_count_chalan=Coalesce(Subquery(
                item_sold_count_chalan, output_field=IntegerField()
            ), 0),
            item_category_name=F('item_category__name')
        ).annotate(
            item_sold_count=F('item_sold_count_sale') + F('item_sold_count_chalan')
        ).values('id', 'name', 'code', 'item_category', 'item_category_name', 'item_sold_count').order_by(
            '-item_sold_count')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = queryset[:3]
        total_items_sold = sum(SaleDetail.objects.filter(ref_sale_detail__isnull=True).values_list('qty', flat=True))
        total_items_returned = sum(
            SaleDetail.objects.filter(ref_sale_detail__isnull=False).values_list('qty', flat=True))
        data = {"pages": page, "total_items_sold": total_items_sold - total_items_returned}
        return Response(data, status=status.HTTP_200_OK)


class PurchaseSaleLineCartListAPIView(APIView):
    permission_classes = [AllDashBoardPermission]

    def get_queryset(self, *args, **kwargs):
        data = {
            "date": [],
            "purchase_amount": [],
            "sale_amount": [],
        }
        current_fiscal_year = int(get_full_fiscal_year_code_bs().split('/')[0])
        start_date_bs = nepali_datetime.date(current_fiscal_year, 4, 1)

        start_date_ad = start_date_bs.to_datetime_date()
        current_date_ad = timezone.now().date().replace(day=1)

        purchases = PurchaseMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                                  created_date_ad__lte=timezone.now()).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            purchase_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'purchase_amount').order_by('date')

        sales = SaleMaster.objects.filter(created_date_ad__gte=start_date_ad,
                                          created_date_ad__lte=timezone.now()).annotate(
            date=ExtractMonth('created_date_ad')
        ).values('date').annotate(
            sale_amount=Coalesce(Sum('grand_total', output_field=DecimalField()), Decimal("0.00"))
        ).values('date', 'sale_amount').order_by('date')

        while current_date_ad >= start_date_ad:
            month = current_date_ad.month
            purchase_data = 0.00
            sales_data = 0.00

            purchase_amount = purchases.filter(date=current_date_ad.month).values_list('purchase_amount', flat=True)
            if purchase_amount:
                purchase_data = purchase_amount[0]

            sale_amount = sales.filter(date=current_date_ad.month).values_list('sale_amount', flat=True)
            if sale_amount:
                sales_data = sale_amount[0]

            data['date'].append(month)
            data['purchase_amount'].append(purchase_data)
            data['sale_amount'].append(sales_data)

            current_date_ad -= relativedelta(months=1)

        data['date'].reverse()
        data['purchase_amount'].reverse()
        data['sale_amount'].reverse()
        return data

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        return Response(queryset, status=status.HTTP_200_OK)

# for pdf and excel
# from rest_framework.viewsets import ReadOnlyModelViewSet
# from rest_framework.renderers import JSONRenderer
# from drf_renderer_xlsx.renderers import XLSXRenderer
# from drf_renderer_xlsx.mixins import XLSXFileMixin
# from rest_framework.renderers import JSONRenderer
# from rest_framework.response import Response
# from rest_framework.views import APIView


# class MyExcelViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
#     queryset = Item.objects.all()
#     serializer_class = ItemSerializer
#     xlsx_ignore_headers = [
#         'created_date_bs','created_date_ad','stock_alert_qty','location','image','expirable',\
#         'item_category','taxable', 'discountable', 'item_type_display', 'basic_info', 'item_type_display',\
#             'created_by', 'active','item_type'
#         ]
#     column_header = {
#         'titles': [
#             "S.N.",
#             "Category",
#             "Name", "Code", "TAX %", 'Purchase cost', "Sale cost","Profit"
#         ],}

#     renderer_classes = [XLSXRenderer]
#     filename = 'file.xlsx'

#     def get_queryset(self):
#         queryset = Item.objects.all()
#         code = self.request.query_params.get('code', None)
#         if code is not None:
#             queryset = queryset.filter(code=code)
#         return queryset
#     def get_header(self):
#         return {
#             'tab_title': 'Item Report',
#             'header_title': 'Item Report',
#             'height': 20,
#             'style': {
#                 'fill': {
#                     'fill_type': 'solid',
#                     'start_color': 'FFFFFFFF',
#                 },
#                 'alignment': {
#                     'horizontal': 'center',
#                     'vertical': 'center',
#                     'wrapText': True,
#                     'shrink_to_fit': True,
#                 },
#                 'border_side': {
#                     'border_style': 'thin',
#                     'color': 'FF000000',
#                 },
#                 'font': {
#                     'name': 'Arial',
#                     'size': 14,
#                     'bold': True,
#                     'color': 'FF000000',
#                 }
#             }
#         }


# from django.views.generic import ListView
# from django.http import HttpResponse
# from django.template.loader import get_template 
# from xhtml2pdf import pisa
# from django.views.generic import View

# class SaleMasterPDFView(View):
#     def get(self, request, *args, **kwargs):
#         template_name = 'sale.html'
#         purchase_master = PurchaseMaster.objects.all()
#         total =  PurchaseMaster.objects.aggregate(
#             total_discount=Coalesce(Sum('total_discount'), 0),
#             grand_total =Coalesce(Sum('grand_total'),0)
#         )
#         print(total)

#         context = {
#             "purchase_masters": purchase_master,
#             "totals": total

#         }

#         # Create a Django response object, and specify content_type as pdf
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'filename="report.pdf"'
#         # find the template and render it.
#         template = get_template(template_name)
#         html = template.render(context)

#         # create a pdf
#         pisa_status = pisa.CreatePDF(html, dest=response)
#         # if error then show some funy purchase_order_view
#         if pisa_status.err:
#             return HttpResponse('We had some errors <pre>' + html + '</pre>')
#         return response
