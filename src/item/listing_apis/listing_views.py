from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.warehouse_location.models import Location
from .listing_serializers import (ItemGenericNameListSerializer, ItemItemCategoryListSerializer,
                                  ItemManufacturerListSerializer, ItemUnitListSerializer,
                                  PackingTypeDetailItemListSerializer, ItemLocationListSerializer,
                                  PackingTypeDetailPackingTypeListSerializer)
from ..item_permissions import ItemPermission
from ..models import GenericName, Item, ItemCategory, Manufacturer, PackingType, Unit


class GenericNameListApiView(ListAPIView):
    permission_classes = [ItemPermission]
    queryset = GenericName.objects.filter(active=True)
    serializer_class = ItemGenericNameListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class ItemCategoryListApiView(ListAPIView):
    permission_classes = [ItemPermission]
    queryset = ItemCategory.objects.filter(active=True)
    serializer_class = ItemItemCategoryListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


class ManufacturerListApiView(ListAPIView):
    permission_classes = [ItemPermission]
    queryset = Manufacturer.objects.filter(active=True)
    serializer_class = ItemManufacturerListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', ]
    ordering_fields = ['id', 'name']


class UnitListApiView(ListAPIView):
    permission_classes = [ItemPermission]
    queryset = Unit.objects.filter(active=True)
    serializer_class = ItemUnitListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'short_form']
    ordering_fields = ['id', 'name', 'short_form']


class PackingTypeListApiView(ListAPIView):
    permission_classes = [ItemPermission]
    queryset = PackingType.objects.filter(active=True)
    serializer_class = PackingTypeDetailPackingTypeListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'short_name']
    ordering_fields = ['id', 'name', 'short_name']


class ItemListApiView(ListAPIView):
    permission_classes = [ItemPermission]
    queryset = Item.objects.filter(active=True)
    serializer_class = PackingTypeDetailItemListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


class ItemLocationFilter(filters.FilterSet):
    item = filters.NumberFilter(
        field_name="location_pack_codes__purchase_detail__item__id",
        label="item",
        distinct=True
    )

    class Meta:
        model = Location
        fields = ['item']


class ItemLocationListApiView(ListAPIView):
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    permission_classes = [ItemPermission]
    filter_class = ItemLocationFilter
    search_fields = ['code']
    ordering_fields = ['id']
    serializer_class = ItemLocationListSerializer

    def get_queryset(self):
        parent_ids = list(Location.objects.exclude(parent=None).values_list('parent', flat=True))
        queryset = Location.objects.exclude(id__in=parent_ids).values("id", "code", "name")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
