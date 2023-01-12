from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from .chalan_stock_serializers import ChalanDetailStockSerializer
from .models import ChalanDetail


class ChalanStockDetailApiView(ListAPIView):
    serializer_class = ChalanDetailStockSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['item__name']
    ordering_fields = ['id']
    filter_fields = ['chalan_master', 'item']

    def get_queryset(self):
        queryset = ChalanDetail.objects.filter(
            ref_chalan_detail__isnull=True
        ).prefetch_related(Prefetch(
            'chalan_packing_types',
            queryset=SalePackingTypeCode.objects.filter(
                sale_packing_type_detail_code__salepackingtypedetailcode__isnull=True

            ).distinct('id').prefetch_related(Prefetch(
                'sale_packing_type_detail_code',
                queryset=SalePackingTypeDetailCode.objects.filter(
                    salepackingtypedetailcode__isnull=True
                )
            )
            )
        )
        ).select_related("chalan_master", "item",
                         "item_category")
        return queryset
