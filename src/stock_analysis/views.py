from decimal import Decimal

import django_filters
from django.db.models import OuterRef, Subquery, Sum, F, Q, DecimalField, Count
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.custom_lib.functions.stock import get_item_ledger
from src.customer_order.models import OrderDetail
from src.item.models import Item
from src.item_serialization.models import PackingTypeCode
from src.item_serialization.services.pack_and_serial_info import find_available_pack_in_item
from src.purchase.models import PurchaseDetail
from src.sale.models import SaleDetail
from src.supplier.models import Supplier
from src.warehouse_location.models import Location
from .serializers import (PurchaseDetailStockSerializer,
                          StockAnalysisSerializer, GetStockByBatchSerializer, ItemListSerializer, ItemLedgerSerializer,
                          RemainingItemCostSerialzier)
from .stock_analysis_permissions import StockAnalysisPermission, ItemLedgerPermission
from ..chalan.models import ChalanDetail
from ..item_serialization.serialization_permissions import PacketInfoPermission, RemainingPacketInfoPermission
from ..transfer.models import TransferDetail


class FilterForPurchaseDetailStock(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    expiry_date = django_filters.DateFromToRangeFilter(field_name="expiry_date_ad")

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'purchase', 'purchase__supplier', 'item']


class FilterForItemList(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = Item
        fields = ['id', 'name', 'date']


class PurchaseDetailStockViewSet(viewsets.ModelViewSet):
    queryset = PurchaseDetail.objects.filter(
        ref_purchase_detail__isnull=True
    ).select_related(
        'item', 'purchase',
        'item_category',
        'packing_type_detail'
    )
    permission_classes = [StockAnalysisPermission]
    serializer_class = PurchaseDetailStockSerializer
    filter_class = FilterForPurchaseDetailStock
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'expiry_date_ad', 'item__name']
    search_fields = ['item__name', 'item__code']


class FilterForStockAnalysisReport(django_filters.FilterSet):
    supplier = django_filters.ModelChoiceFilter(
        field_name="purchasedetail__purchase__supplier",
        label="supplier",
        queryset=Supplier.objects.all()
    )
    location = django_filters.ModelChoiceFilter(
        field_name="purchasedetail__pu_pack_type_codes__location",
        label="location",
        queryset=Location.objects.all(),
        distinct=True
    )

    class Meta:
        model = Item
        fields = ['id', 'name', 'supplier']


class StockAnalysisView(ListAPIView):
    permission_classes = [StockAnalysisPermission]
    serializer_class = StockAnalysisSerializer
    filter_class = FilterForStockAnalysisReport
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ['name', 'code', 'item_category__name']
    ordering_fields = ['id']

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
        transfer_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            transfer_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=1,
                                                             transferdetail__cancelled=False))
        ).values("transfer_qty")
        transfer_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
            transfer_return_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=2,
                                                                    transferdetail__cancelled=False))
        ).values("transfer_return_qty")
        queryset = Item.objects.filter(active=True).annotate(
            purchase_qty=Coalesce(
                Subquery(purchase_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            purchase_return_qty=Coalesce(
                Subquery(purchase_return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            sale_qty=Coalesce(
                Subquery(sale_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            sale_return_qty=Coalesce(
                Subquery(sale_return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            pending_customer_order_qty=Coalesce(
                Subquery(pending_customer_order_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            asset_count=Subquery(
                asset_count, output_field=DecimalField()
            ),
            chalan_qty=Coalesce(
                Subquery(chalan_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            chalan_return_qty=Coalesce(
                Subquery(chalan_return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            transfer_qty=Coalesce(
                Subquery(transfer_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            transfer_return_qty=Coalesce(
                Subquery(transfer_return_qty, output_field=DecimalField()), Decimal("0.00")
            )

        ).filter(purchase_qty__gt=0).annotate(
            remaining_qty=F('purchase_qty') - F('purchase_return_qty') - F('sale_qty') - F('pending_customer_order_qty') \
                          + F('sale_return_qty') - F('asset_count') - F('chalan_qty') + F('chalan_return_qty') -
                          F("transfer_qty") + F("transfer_return_qty"),
            transfer_qty=F('transfer_qty') - F('transfer_return_qty')
        ).values(
            'id', 'purchase_cost', 'sale_cost', 'name', 'discountable',
            'taxable', 'tax_rate', 'code', 'item_category', 'purchase_qty', 'purchase_return_qty',
            'sale_qty', 'sale_return_qty', 'pending_customer_order_qty', 'chalan_qty', 'chalan_return_qty',
            'transfer_qty',
            'remaining_qty')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class ItemLedgerView(ListAPIView):
    permission_classes = [ItemLedgerPermission]
    queryset = PurchaseDetail.objects.all()
    serializer_class = ItemLedgerSerializer

    def list(self, request):
        query_dict = {

        }
        for k, vals in request.GET.lists():
            if vals[0] != '':
                k = str(k)
                if k == 'date_after':
                    k = 'created_date_ad__date__gte'
                elif k == 'date_before':
                    k = 'created_date_ad__date__lte'
                if k != "limit" and k != "offset":
                    query_dict[k] = vals[0]
        data = get_item_ledger(query_dict)
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data, status=status.HTTP_200_OK)


class ExpiredItemView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [StockAnalysisPermission]
    queryset = PurchaseDetail.objects.filter(ref_purchase_detail__isnull=True)
    serializer_class = PurchaseDetailStockSerializer
    filter_class = FilterForPurchaseDetailStock
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id']
    search_fields = ['item__name']
    filter_fields = ['id', 'purchase', 'purchase__supplier', 'item']


class GetStockByBatchViewSet(ListAPIView):
    permission_classes = [StockAnalysisPermission]
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ['batch_no']
    ordering_fields = ['id']
    filterset_fields = ['item', 'id']
    serializer_class = GetStockByBatchSerializer

    def get_queryset(self):
        asset_count = PurchaseDetail.objects.filter(pk=OuterRef("pk"), ref_purchase_detail__isnull=True).annotate(
            asset_count=Count(
                'pu_pack_type_codes__pack_type_detail_codes__assetlist'
            )
        ).values('asset_count')
        purchase_return_qty = PurchaseDetail.objects.filter(ref_purchase_detail=OuterRef("pk")).values(
            "ref_purchase_detail"
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

        sale_return_qty = SaleDetail.objects.filter(
            ref_purchase_detail=OuterRef("pk"), sale_master__sale_type=2, sale_master__return_dropped=True).annotate(
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
            ref_purchase_detail=OuterRef("pk"), chalan_master__status=3, chalan_master__return_dropped=True
        ).values("ref_purchase_detail").annotate(
            chalan_return_qty=Sum(
                'qty'
            )
        ).values('chalan_return_qty')

        pending_customer_order_qty = OrderDetail.objects.filter(
            purchase_detail=OuterRef("pk"), order__status=1, cancelled=False
        ).values("purchase_detail").annotate(
            pending_customer_order_qty=Sum(
                'qty'
            )
        ).values('pending_customer_order_qty')

        queryset = PurchaseDetail.objects.filter(
            ref_purchase_detail__isnull=True
        ).annotate(
            purchase_return_qty=Coalesce(
                Subquery(purchase_return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            sale_qty=Coalesce(
                Subquery(sale_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            sale_return_qty=Coalesce(
                Subquery(sale_return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            pending_customer_order_qty=Coalesce(
                Subquery(pending_customer_order_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            asset_count=Subquery(
                asset_count, output_field=DecimalField()
            ),
            chalan_qty=Coalesce(
                Subquery(chalan_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            chalan_return_qty=Coalesce(
                Subquery(chalan_return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            transfer_qty=Coalesce(
                Subquery(transfer_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            transfer_return_qty=Coalesce(
                Subquery(transfer_return_qty, output_field=DecimalField()), Decimal("0.00")
            )).annotate(
            remaining_qty=
            F('qty') - F('purchase_return_qty') - F('sale_qty') + F('sale_return_qty')
            - F('pending_customer_order_qty') - F('asset_count') - F('chalan_qty') + F('chalan_return_qty')
            - F('transfer_qty') + F('transfer_return_qty')

        ).values("id", "batch_no", "qty",
                 "remaining_qty", "purchase_cost", "purchase_return_qty",
                 "sale_qty", "sale_return_qty", "pending_customer_order_qty", "asset_count",
                 "chalan_qty", "chalan_return_qty", "transfer_qty", "transfer_return_qty", "item")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class RemainingItemCostListView(ListAPIView):
    permission_classes = [StockAnalysisPermission]
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    # search_fields = ['item__name']
    ordering_fields = ['item']
    filterset_fields = ['item']
    serializer_class = RemainingItemCostSerialzier

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
            ref_purchase_detail=OuterRef("pk"), sale_master__sale_type=2, sale_master__return_dropped=True).values(
            "ref_purchase_detail").annotate(
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
            ref_purchase_detail=OuterRef("pk"), chalan_master__status=3, chalan_master__return_dropped=True
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
            ref_purchase_detail=OuterRef("pk"), transfer_master__transfer_type=1
        ).values("ref_purchase_detail").annotate(
            transfer_qty=Sum('qty')
        ).values("transfer_qty")
        transfer_return_qty = TransferDetail.objects.filter(
            ref_purchase_detail=OuterRef("pk"), transfer_master__transfer_type=2
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
            )

        ).filter(remaining_qty__gt=0).values("item", "item__name"
                                             ).annotate(
            total_remaining_qty=Sum("remaining_qty"),
            total_remaining_cost=Sum(F('remaining_qty') * F('purchase_cost'))

        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class ItemListAPIView(ListAPIView):
    permission_classes = [StockAnalysisPermission]
    queryset = Item.objects.filter(active=True)
    serializer_class = ItemListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_class = FilterForItemList
    ordering_fields = ['id']
    search_fields = ['name']


class ItemRemainingPackingTypeDetails(ListAPIView):
    permission_classes = [RemainingPacketInfoPermission]
    queryset = PackingTypeCode.objects.all()

    def list(self, request, *args, **kwargs):
        item_id = kwargs.get("item_id", None)

        try:
            Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"item_id": "does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(find_available_pack_in_item(item_id=item_id))

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset)
