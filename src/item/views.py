# Django-Rest_framework
import django_filters
from django.db import transaction
from django_filters.rest_framework import DateFromToRangeFilter, DjangoFilterBackend, FilterSet
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from simple_history.utils import update_change_reason

from .item_permissions import ItemPermission
# imported models
from .models import GenericName, Item, ItemCategory, Manufacturer, PackingType, PackingTypeDetail, Unit
# imported serializer
from .serializers import (GenericNameSerializer, ItemCategorySerializer, ItemCreateSerializer, ItemViewSerializer,
                          ManufacturerSerializer, PackingTypeDetailCreateSerializer,
                          PackingTypeDetailViewSerializer, PackingTypeSerializer, UnitSerializer)


# for log


# views
# custom filter for Unit model

class FilterForPackingType(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = PackingType
        fields = ['name', 'short_name']


class PackingTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = PackingType.objects.all()
    serializer_class = PackingTypeSerializer
    filter_class = FilterForPackingType
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'short_name']
    ordering_fields = ['id', 'name']
    http_method_names = ['get', 'head', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForUnit(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Unit
        fields = ['name', 'active', 'short_form']


class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filter_class = FilterForUnit
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'short_form']
    ordering_fields = ['id', 'name', 'short_form']
    http_method_names = ['get', 'head', 'post', 'patch']


# custom filter for Manufacturer model
class FilterForManufacturer(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Manufacturer
        fields = ['name', 'active']


class ManufacturerViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = Manufacturer.objects.all()
    # print(queryset.query)
    serializer_class = ManufacturerSerializer
    filter_class = FilterForManufacturer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    http_method_names = ['get', 'head', 'post', 'patch']


# custom filter for Genericname model
class FilterForGenericName(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = GenericName
        fields = ['name', 'active']


class GenericNameViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = GenericName.objects.all()
    serializer_class = GenericNameSerializer
    filter_class = FilterForGenericName
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    http_method_names = ['get', 'head', 'post', 'patch']


# custom filter for Item model
class FilterForItem(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Item
        fields = ['code', 'item_category__name', 'manufacturer', 'generic_name',
                  'location', 'taxable', 'discountable', 'fixed_asset']


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = Item.objects.all().select_related("item_category", "manufacturer", "generic_name", "unit")
    filter_class = FilterForItem
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']
    http_method_names = ['get', 'head', 'post', 'patch']

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            serializer_class = ItemCreateSerializer
        elif self.request.method == 'GET':
            serializer_class = ItemViewSerializer
        return serializer_class

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(ItemViewSet, self).create(request)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForItemCategory(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = ItemCategory
        fields = ['display_order', 'active', 'code', 'date', 'name']


class ItemCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    filter_class = FilterForItemCategory
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code', 'display_order']
    http_method_names = ['get', 'head', 'post', 'patch']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForPackingTypeDetail(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    item__name = django_filters.CharFilter(lookup_expr='iexact')
    packing_type__name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = PackingTypeDetail
        fields = ['id', 'item', 'packing_type']


class PackingTypeDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = PackingTypeDetail.objects.all().select_related("item", "packing_type")
    filter_class = FilterForPackingTypeDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['item__name', 'packing_type__name']
    ordering_fields = ['id', 'item']
    http_method_names = ['get', 'head', 'post', 'patch']

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            serializer_class = PackingTypeDetailCreateSerializer
        elif self.request.method == 'GET':
            serializer_class = PackingTypeDetailViewSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. Atleast one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
