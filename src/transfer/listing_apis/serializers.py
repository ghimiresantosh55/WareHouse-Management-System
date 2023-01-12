from rest_framework import serializers

from src.item.models import PackingTypeDetail


class TransferItemPackingTypeListSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)

    class Meta:
        model = PackingTypeDetail
        fields = ['id', 'item', 'packing_type_name', 'pack_qty', 'packing_type']
