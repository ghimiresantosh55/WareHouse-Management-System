from rest_framework import serializers

from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from .models import PurchaseDetail


class PackingTypeDetailCodePurchaseDetailAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        fields = ['id', 'code']
        read_only_fields = fields


class PackingTypeCodePurchaseDetailAvailableSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = PackingTypeDetailCodePurchaseDetailAvailableSerializer(many=True)

    class Meta:
        model = PackingTypeCode
        fields = ['pack_type_detail_codes', 'code', 'id', 'purchase_order_detail']
        read_only_fields = fields


class PurchaseDetailAvailableSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = PackingTypeCodePurchaseDetailAvailableSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    remaining_qty = serializers.IntegerField(read_only=True)
    is_serializable = serializers.ReadOnlyField(source='item.is_serializable', allow_null=True)
    item_unit = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'remaining_qty', 'item', 'item_category', 'pu_pack_type_codes',
                  'purchase_cost', 'sale_cost', 'packing_type', 'packing_type_detail',
                  'purchase', 'pack_qty', 'packing_type_name', 'taxable', 'discountable',
                  'item_name', 'batch_no', 'tax_rate', 'is_serializable',
                  'discount_rate', 'item_unit']
        read_only_fields = fields
