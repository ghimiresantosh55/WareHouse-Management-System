from decimal import Decimal

from django.db.models import OuterRef, Count, Sum, DecimalField, F, Subquery
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.item.models import Item
from src.purchase.models import PurchaseMaster, PurchaseDetail
from src.supplier.models import Supplier
from .listing_serializers import SupplierListSerializer, PurchaseListSerializer, ItemListStockSerializer, \
    ItemListStockSubtractionListSerializer, BatchStockSubtractionSerializer
from ...chalan.models import ChalanDetail
from ...customer_order.models import OrderDetail
from ...sale.models import SaleDetail
from ...transfer.models import TransferDetail


class SupplierListAPIView(ListAPIView):
    queryset = Supplier.objects.filter(active=True)
    serializer_class = SupplierListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    filter_fields = ['name']
    search_fields = ['id', 'name']


class PurchaseListAPIView(ListAPIView):
    queryset = PurchaseMaster.objects.filter(purchase_type=1)
    serializer_class = PurchaseListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    filter_fields = ['purchase_no']
    search_fields = ['id', 'purchase_no']


class ItemListAPIView(ListAPIView):
    queryset = Item.objects.filter(active=True)
    serializer_class = ItemListStockSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    filter_fields = ['name', 'code']
    search_fields = ['id', 'name', 'code']


class ItemStockSubtractionListAPIView(ListAPIView):
    queryset = Item.objects.filter(active=True)
    serializer_class = ItemListStockSubtractionListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    filter_fields = ['name']
    search_fields = ['id', 'name']


class BatchNoStockSubtractionListAPIView(ListAPIView):
    queryset = PurchaseDetail.objects.all()
    serializer_class = BatchStockSubtractionSerializer
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ['batch_no']
    ordering_fields = ['id']
    filter_fields = ['item']

    def get_queryset(self):
        asset_count = PurchaseDetail.objects.filter(pk=OuterRef("pk"), ref_purchase_detail__isnull=True).annotate(
            asset_count=Count(
                'pu_pack_type_codes__pack_type_detail_codes__assetlist'
            )
        ).values('asset_count')
        purchase_return_qty = PurchaseDetail.objects.filter(self_ref_purchase_detail=OuterRef("pk")).values(
            "self_ref_purchase_detail"
        ).annotate(
            purchase_return_qty=Sum(
                'qty',
                output_field=DecimalField()
            )
        ).values('purchase_return_qty')

        sale_qty = SaleDetail.objects.filter(ref_purchase_detail=OuterRef("pk"), sale_master__sale_type=1).values(
            "ref_purchase_detail").annotate(
            sale_qty=Sum(
                'qty'
            )
        ).values('sale_qty')

        sale_return_qty = SaleDetail.objects.filter(
            ref_purchase_detail=OuterRef("pk"), sale_master__sale_type=2).annotate(
            sale_return_qty=Sum(
                'qty'
            )
        ).values('sale_return_qty')

        chalan_qty = ChalanDetail.objects.filter(
            ref_purchase_detail=OuterRef("pk"), chalan_master__status=1
        ).values("ref_purchase_detail").annotate(
            chalan_qty=Sum(
                'qty'
            )
        ).values('chalan_qty')

        chalan_return_qty = ChalanDetail.objects.filter(
            ref_purchase_detail=OuterRef("pk"), chalan_master__status=3
        ).values("ref_purchase_detail").annotate(
            chalan_return_qty=Sum(
                'qty'
            )
        ).values('chalan_return_qty')

        pending_customer_order_qty = OrderDetail.objects.filter(
            purchase_detail=OuterRef("pk"), order__status=1
        ).values("purchase_detail").annotate(
            pending_customer_order_qty=Sum(
                'qty'
            )
        ).values('pending_customer_order_qty')
        transfer_qty = TransferDetail.objects.filter(
            ref_purchase_detail=OuterRef("pk"), transfer_master__transfer_type=1, cancelled=False
        ).values("ref_purchase_detail").annotate(
            transfer_qty=Sum('qty')
        ).values("transfer_qty")
        transfer_return_qty = TransferDetail.objects.filter(
            ref_purchase_detail=OuterRef("pk"), transfer_master__transfer_type=2, cancelled=False
        ).values("ref_purchase_detail").annotate(
            transfer_return_qty=Sum('qty')
        ).values("transfer_return_qty")
        queryset = PurchaseDetail.objects.filter(
            ref_purchase_detail__isnull=True
        ).annotate(
            remaining_qty=
            F('qty')
            - Coalesce(
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
            purchase_no=F('purchase__purchase_no'),
            packing_type_name=F('packing_type__name'),
        ).filter(remaining_qty__gt=0).values("id", "batch_no", "qty",
                                             "remaining_qty", "purchase_cost", "sale_cost", "purchase_no",
                                             "net_amount", "gross_amount", "pack_qty",
                                             "packing_type", "packing_type_name", "packing_type_detail",
                                             "taxable", "tax_rate", "tax_amount",
                                             "discountable", "expirable", "discount_rate",
                                             "discount_amount")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
