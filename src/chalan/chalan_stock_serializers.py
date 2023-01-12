from rest_framework import serializers

from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from .models import ChalanDetail
from .services import chalan_stock


class ChalanStockPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source="packing_type_detail_code.code", allow_null=True)

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'code']
        read_only_fields = fields


class ChalanStockPackingTypeCodeSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = ChalanStockPackingTypeDetailCodeSerializer(many=True)
    code = serializers.ReadOnlyField(source="packing_type_code.code", allow_null=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'packing_type_code', 'code',
                  'sale_packing_type_detail_code', 'customer_order_detail']
        read_only_fields = fields


class ChalanDetailStockSerializer(serializers.ModelSerializer):
    chalan_packing_types = ChalanStockPackingTypeCodeSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')
    code_name = serializers.ReadOnlyField(source='item.code')
    unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    batch_no = serializers.ReadOnlyField(source='ref_purchase_detail.batch_no')
    return_qty = serializers.SerializerMethodField()
    remaining_qty = serializers.SerializerMethodField()

    class Meta:
        model = ChalanDetail
        exclude = ['created_date_ad', 'created_date_bs', 'ref_chalan_detail', 'created_by']

    @staticmethod
    def get_return_qty(chalan):
        chalan_id = chalan.id
        qty = chalan_stock.get_chalan_detail_returned_qty(chalan_id)
        return qty

    @staticmethod
    def get_remaining_qty(chalan):
        chalan_id = chalan.id
        qty = chalan_stock.get_chalan_detail_remaining_qty(chalan_id)
        return qty

    def to_representation(self, instance):
        return_amount_data = chalan_stock.get_chalan_detail_returned_amounts(instance.id)
        data = super(ChalanDetailStockSerializer, self).to_representation(instance)
        data['discount_amount'] = instance.discount_amount - return_amount_data['return_discount_amount']
        data['tax_amount'] = instance.tax_amount - return_amount_data['return_tax_amount']
        data['gross_amount'] = instance.gross_amount - return_amount_data['return_gross_amount']
        data['net_amount'] = instance.net_amount - return_amount_data['return_net_amount']

        return data
