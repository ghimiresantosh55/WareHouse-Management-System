from src.item.models import Item, ItemCategory, Unit
from rest_framework import serializers


class PPBItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'code']


class PPBItemCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'code']


class PPBItemUnitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'short_form']


