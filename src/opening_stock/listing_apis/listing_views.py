from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from src.core_app.models import Country
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail
from .listing_serializers import (OpeningStockPackingTypeDetailListSerializer, OpeningStockItemCategoryListSerializer,
                                  OpeningStockCountryListSerializer, OpeningStockPackingTypeListSerializer,
                                  OpeningStockItemListSerializer)


class CountryListApiView(ListAPIView):
    # permission_classes = [ItemListPermission]
    queryset = Country.objects.filter(active=True)
    serializer_class = OpeningStockCountryListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class ItemCategoryListApiView(ListAPIView):
    # permission_classes = [ItemListPermission]
    queryset = ItemCategory.objects.filter(active=True)
    serializer_class = OpeningStockItemCategoryListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


class PackingTypeListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = PackingType.objects.filter(active=True)
    serializer_class = OpeningStockPackingTypeListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'short_name']
    ordering_fields = ['id', 'name', 'short_name']


class ItemListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = Item.objects.filter(active=True)
    serializer_class = OpeningStockItemListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


class PackingTypeDetailListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = PackingTypeDetail.objects.filter(active=True).select_related('packing_type')
    serializer_class = OpeningStockPackingTypeDetailListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id']
    filter_fields = ['item', 'packing_type']
