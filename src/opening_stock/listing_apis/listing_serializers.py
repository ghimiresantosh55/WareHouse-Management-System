from rest_framework import serializers

from src.core_app.models import Country
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail


class OpeningStockCountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class OpeningStockItemCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'code']


class OpeningStockItemListSerializer(serializers.ModelSerializer):
    item_category = OpeningStockItemCategoryListSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'code', 'item_category', 'discountable',
                  'taxable', 'tax_rate', 'purchase_cost']


class OpeningStockPackingTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingType
        fields = ['id', 'name', 'short_name']


class OpeningStockPackingTypeDetailListSerializer(serializers.ModelSerializer):
    packing_type = OpeningStockPackingTypeListSerializer(read_only=True)

    class Meta:
        model = PackingTypeDetail
        fields = ['id', 'item', 'packing_type', 'pack_qty']
