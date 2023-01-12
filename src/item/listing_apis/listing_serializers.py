from rest_framework import serializers

from ..models import GenericName, Item, ItemCategory, Manufacturer, PackingType, Unit


class ItemItemCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'code']


class ItemManufacturerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name']


class ItemGenericNameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericName
        fields = ['id', 'name']


class ItemUnitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'short_form']


class PackingTypeDetailItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'code']


class PackingTypeDetailPackingTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingType
        fields = ['id', 'name']


class ItemLocationListSerializer(serializers.Serializer):
    parent_ids = serializers.ListField(read_only=True)
