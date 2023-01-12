from rest_framework import serializers
from src.item.models import PackingType, PackingTypeDetail


class StockAdjustmentPackingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingType
        fields = ['id', 'name', 'short_name']


class StockAdjustmentPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type = StockAdjustmentPackingTypeSerializer(read_only=True)

    class Meta:
        model = PackingTypeDetail
        fields = ['id', 'item', 'packing_type', 'pack_qty', 'created_date_ad', 'created_date_bs']
