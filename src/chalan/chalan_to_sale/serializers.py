from rest_framework import serializers

from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from ..models import ChalanMaster, ChalanDetail
from ..serializers import ChalanSummaryItemSerializer, ChalanSummaryCustomerSerializer, ChalanSummaryDiscountScheme


class PackingTypeDetailCodeChalanSaleViewSerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source='packing_type_detail_code.code')

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'code']
        read_only_fields = fields


class PackingTypeCodeChalanSaleViewSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = PackingTypeDetailCodeChalanSaleViewSerializer(many=True)
    code = serializers.ReadOnlyField(source='packing_type_code.code', allow_null=True)
    location_code = serializers.ReadOnlyField(source='packing_type_code.location.code', allow_null=True)
    location = serializers.ReadOnlyField(source='packing_type_code.location.id', allow_null=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'location_code', 'location', 'code',
                  'packing_type_code', 'sale_packing_type_detail_code']
        read_only_fields = fields


class ChalanDetailSummarySaleSerializer(serializers.ModelSerializer):
    item = ChalanSummaryItemSerializer(read_only=True)
    chalan_packing_types = PackingTypeCodeChalanSaleViewSerializer(many=True, read_only=True)
    returned_qty = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = ChalanDetail
        fields = ['id', 'item', 'item_category', 'qty', 'returned_qty', 'sale_cost',
                  'discountable', 'taxable', 'tax_rate', 'tax_amount',
                  'discount_rate', 'discount_amount', 'gross_amount', 'net_amount',
                  'ref_purchase_detail',
                  'ref_order_detail', 'remarks', 'chalan_packing_types'
                  ]
        read_only_fields = fields


class ChalanMasterSummarySaleSerializer(serializers.ModelSerializer):
    customer = ChalanSummaryCustomerSerializer(read_only=True)
    discount_scheme = ChalanSummaryDiscountScheme(read_only=True)
    chalan_details = ChalanDetailSummarySaleSerializer(many=True, read_only=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no', 'status', 'customer', 'discount_scheme',
                  'discount_rate',
                  'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'ref_order_master', 'grand_total', 'remarks', 'created_date_ad',
                  'created_date_bs', 'created_by', 'created_by_user_name', 'status_display',
                  'chalan_details']
