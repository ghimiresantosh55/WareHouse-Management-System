from decimal import Decimal

import django_filters
from django.db.models import OuterRef, Count, Sum, Q, Max, Subquery, DecimalField
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.customer.models import Customer
from src.item.models import Item
from .listing_serializers import (CustomerQuotationListSerializer, ItemQuotationListSerializer,
                                  RemainingItemQuotationListSerializer)
from ...purchase.models import PurchaseDetail


class CustomerListApiView(ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerQuotationListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'middle_name', 'last_name', 'pan_vat_no']
    ordering_fields = ['id', 'first_name']


class ItemListApiView(ListAPIView):
    serializer_class = ItemQuotationListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    queryset = Item.objects.all()


class ItemListFilterForQuotation(django_filters.FilterSet):
    id = django_filters.ModelMultipleChoiceFilter(queryset=Item.objects.filter(active=True),
                                                  to_field_name='id')

    class Meta:
        model = Item
        fields = ['id', 'name']


class RemainingItemListAPIVIew(ListAPIView):
    serializer_class = RemainingItemQuotationListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = ItemListFilterForQuotation
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        asset_count = Item.objects.filter(pk=OuterRef("pk")).annotate(
            asset_count=Count(
                'purchasedetail__pu_pack_type_codes__pack_type_detail_codes__assetlist',
                filter=Q(purchasedetail__ref_purchase_detail__isnull=True)
            )
        ).values('asset_count')
        purchase_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            purchase_qty=Sum(
                'purchasedetail__qty',
                filter=Q(purchasedetail__purchase__purchase_type__in=[1, 3, 4])
            )
        ).values('purchase_qty')

        purchase_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            purchase_return_qty=Sum(
                'purchasedetail__qty',
                filter=Q(purchasedetail__purchase__purchase_type__in=[2, 5])
            )
        ).values('purchase_return_qty')

        sale_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            sale_qty=Sum(
                'saledetail__qty',
                filter=Q(saledetail__sale_master__sale_type=1)
            )
        ).values('sale_qty')
        sale_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            sale_return_qty=Sum(
                'saledetail__qty',
                filter=Q(saledetail__sale_master__sale_type=2, saledetail__sale_master__return_dropped=True)
            )
        ).values('sale_return_qty')

        chalan_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            chalan_qty=Sum(
                'chalandetail__qty',
                filter=Q(chalandetail__chalan_master__status=1)
            )
        ).values('chalan_qty')

        chalan_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            chalan_return_qty=Sum(
                'chalandetail__qty',
                filter=Q(chalandetail__chalan_master__status=3, chalandetail__chalan_master__return_dropped=True)
            )
        ).values('chalan_return_qty')

        pending_customer_order_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            pending_customer_order_qty=Sum(
                'orderdetail__qty',
                filter=Q(orderdetail__cancelled=False, orderdetail__order__status=1)
            )
        ).values('pending_customer_order_qty')

        highest_sale_cost = PurchaseDetail.objects.filter(item=OuterRef("id")).values('item').annotate(
            highest_sale_cost=Max("sale_cost")
        ).values("highest_sale_cost")
        transfer_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            transfer_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=1,
                                                             transferdetail__cancelled=False))
        ).values("transfer_qty")
        transfer_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            transfer_return_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=2,
                                                                    transferdetail__cancelled=False))
        ).values("transfer_return_qty")
        queryset = Item.objects.filter(active=True).annotate(
            remaining_qty=Coalesce(
                Subquery(purchase_qty, output_field=DecimalField()), Decimal("0.00")
            ) - Coalesce(
                Subquery(purchase_return_qty, output_field=DecimalField()), Decimal("0.00")
            ) - Coalesce(
                Subquery(sale_qty, output_field=DecimalField()), Decimal("0.00")
            ) + Coalesce(
                Subquery(sale_return_qty, output_field=DecimalField()), Decimal("0.00")
            ) - Coalesce(
                Subquery(pending_customer_order_qty, output_field=DecimalField()), Decimal("0.00")
            ) - Subquery(
                asset_count, output_field=DecimalField()
            ) - Coalesce(
                Subquery(chalan_qty, output_field=DecimalField()), Decimal("0.00")
            ) + Coalesce(
                Subquery(chalan_return_qty, output_field=DecimalField()), Decimal("0.00")
            ) - Coalesce(
                Subquery(transfer_qty, output_field=DecimalField()), Decimal("0.00")
            ) + Coalesce(
                Subquery(transfer_return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            item_sale_cost=Subquery(highest_sale_cost, output_field=DecimalField())
        ).values(
            'id', 'name', 'code', 'item_category',
            'remaining_qty'
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
