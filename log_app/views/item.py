from src.item.models import Unit, Manufacturer, GenericName, ItemCategory, Item, PackingType
from log_app.serializers.item import UnitHistorySerializer, ManufacturerHistorySerializer, GenericNameHistorySerializer,\
      ItemCategoryHistorySerializer, ItemHistorySerializer, PackingTypeHistorySerializer
from rest_framework.filters import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from django_filters.filterset import FilterSet
from django_filters import DateFromToRangeFilter
from log_app.permissions.item_log_permissions import *

# for unit
class FilterForUnitHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = Unit.history.model
        fields = ['id','history_type','history_date_bs']

class UnitHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [UnitHistoryPermission]
    queryset= Unit.history.all()
    serializer_class = UnitHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForUnitHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

# For Packing Type
class FilterForPackingTypeHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = PackingType.history.model
        fields = ['id','history_type','history_date_bs']

class PackingTypeHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PackingTypePermission]
    queryset= PackingType.history.all()
    serializer_class = PackingTypeHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForPackingTypeHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

    
# for manufracturer
class FilterForManufacturerHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = Manufacturer.history.model
        fields = ['id','history_type','history_date_bs']

class ManufacturerHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ManufacturerHistoryPermission]
    queryset= Manufacturer.history.all()
    serializer_class = ManufacturerHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForManufacturerHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


# for generic name 
class FilterForGenericNameHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = GenericName.history.model
        fields = ['id','history_type','history_date_bs']

class GenericNameHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [GenericNameHistoryPermission]
    queryset= GenericName.history.all()
    serializer_class = GenericNameHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForGenericNameHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']

class FilterForItemCategoryHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = ItemCategory.history.model
        fields = ['id','history_type','history_date_bs']

class ItemCategoryHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ItemCategoryHistoryPermission]
    queryset= ItemCategory.history.all()
    serializer_class = ItemCategoryHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForItemCategoryHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']


class FilterForItemHistory(FilterSet):
    date = DateFromToRangeFilter(field_name='history_date', label='History date ad')
    class Meta:
        model = Item.history.model
        fields = ['id','history_type','history_date_bs']

class ItemHistoryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ItemHistoryPermission]
    queryset= Item.history.all()
    serializer_class = ItemHistorySerializer
    http_method_names = ['get', 'option', 'head']
    filter_class = FilterForItemHistory
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id','history_date']
    search_fields = ['id','history_date']