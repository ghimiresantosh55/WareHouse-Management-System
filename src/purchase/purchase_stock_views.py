from decimal import Decimal

from django.db.models import F, Prefetch
from django.db.models import OuterRef, Sum, Count, DecimalField, Q, Subquery
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from .models import PurchaseDetail
from .purchase_stock_serializer import PurchaseDetailAvailableSerializer
from ..transfer.models import TransferDetail


class PurchaseDetailAvailableListView(ListAPIView):
    serializer_class = PurchaseDetailAvailableSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    filter_fields = ['purchase', 'item']

    def get_queryset(self):
        asset_count = PurchaseDetail.objects.filter(pk=OuterRef("pk")).annotate(
            asset_count=Count(
                'pu_pack_type_codes__pack_type_detail_codes__assetlist'
            )
        ).values('asset_count')
        purchase_return_qty = PurchaseDetail.objects.filter(pk=OuterRef("pk")).annotate(
            purchase_return_qty=Sum(
                'self_ref_purchase_detail__qty',
                output_field=DecimalField()
            )
        ).values('purchase_return_qty')

        sale_qty = PurchaseDetail.objects.filter(pk=OuterRef("pk")).annotate(
            sale_qty=Sum(
                'purchase_details__qty',
                filter=Q(purchase_details__sale_master__sale_type=1)
            )
        ).values('sale_qty')

        sale_return_qty = PurchaseDetail.objects.filter(pk=OuterRef("pk")).annotate(
            sale_return_qty=Sum(
                'purchase_details__qty',
                filter=Q(purchase_details__sale_master__sale_type=2)
            )
        ).values('sale_return_qty')

        chalan_qty = PurchaseDetail.objects.filter(pk=OuterRef("pk")).annotate(
            chalan_qty=Sum(
                'chalandetail__qty',
                filter=Q(chalandetail__chalan_master__status=1)
            )
        ).values('chalan_qty')

        chalan_return_qty = PurchaseDetail.objects.filter(pk=OuterRef("pk")).annotate(
            chalan_return_qty=Sum(
                'chalandetail__qty',
                filter=Q(chalandetail__chalan_master__status=3)
            )
        ).values('chalan_return_qty')
        pending_customer_order_qty = PurchaseDetail.objects.filter(pk=OuterRef("pk")).annotate(
            pending_customer_order_qty=Sum(
                'orderdetail__qty',
                filter=Q(orderdetail__order__status=1)
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
            remaining_qty=Coalesce(
                F('qty'), Decimal('0'), output_field=DecimalField()
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
            )

        ).filter(remaining_qty__gt=0).prefetch_related(
            Prefetch('pu_pack_type_codes', queryset=PackingTypeCode.objects.filter(
                pack_type_detail_codes__packingtypedetailcode__isnull=True

            ).distinct('id').prefetch_related(
                Prefetch('pack_type_detail_codes', queryset=PackingTypeDetailCode.objects.filter(
                    assetlist__isnull=True,
                    packingtypedetailcode__isnull=True
                ).filter(
                    Q(pack_type_detail_code_of_sale__isnull=True) |
                    Q(pack_type_detail_code_of_sale__salepackingtypedetailcode__isnull=False)
                )
                         #          .filter(
                         #     Q(pack_type_code__purchase_order_detail__packing_type_detail__isnull=True)|
                         #     Q(pack_type_code__purchase_order_detail__self_purchase_order_detail=False)
                         #     # Q(chalan_packing_type_detail_code__isnull=True) |
                         #     # Q(chalan_packing_type_detail_code__self_ref__isnull=False)
                         # )
                         .distinct('id')
                         )
            )
                     )
        ).select_related('item', 'packing_type')

        return queryset

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs)
        return data

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         purchase_order_serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(purchase_order_serializer.data)

    #     purchase_order_serializer = self.get_serializer(queryset, many=True)
    #     return Response(purchase_order_serializer.data)
    # queryset = self.filter_queryset(self.get_queryset())

    # page = self.paginate_queryset(queryset)
    # if page is not None:
    #     return Response(page, status=status.HTTP_200_OK)
    # return Response(queryset, status=status.HTTP_200_OK)
