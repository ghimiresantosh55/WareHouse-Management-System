from rest_framework import serializers

from src.custom_lib.functions import stock
from src.item.models import Item
from src.purchase.models import PurchaseDetail


# purchase detail purchase_order_serializer for write_only views
class PurchaseDetailStockSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    code_name = serializers.ReadOnlyField(source='item.code')
    unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    remaining_qty = serializers.SerializerMethodField()
    return_qty = serializers.SerializerMethodField()
    sale_qty = serializers.SerializerMethodField()
    sale_return_qty = serializers.SerializerMethodField()

    # def get_qty(self, product):
    #     PurchaseDetail.objects.filter(rem_qty__gt=0.00)
    #     ref_purchase_detail = purchase_detail.id
    #     purchase_order_serializer = stock.get_remaining_qty_of_purchase(ref_purchase_detail)
    #     return purchase_order_serializer.data
    class Meta:
        model = PurchaseDetail
        exclude = ['discount_amount', 'gross_amount', 'tax_amount', 'net_amount', 'created_date_ad',
                   'created_date_bs', 'created_by']

    def get_remaining_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        purchase_rem_qty = stock.get_remaining_qty_of_purchase(ref_purchase_detail)

        return purchase_rem_qty

    def get_return_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        return_rem_qty = stock.get_purchase_return_qty(ref_purchase_detail)
        return return_rem_qty

    def get_sale_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        sale_rem_qty = stock.get_purchase_sale_qty(ref_purchase_detail)
        return sale_rem_qty

    def get_sale_return_qty(self, purchase_detail):
        ref_purchase_detail = purchase_detail.id
        rem_qty = stock.get_purchase_sale_return_qty(ref_purchase_detail)
        return rem_qty


class StockAnalysisSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, read_only=True)
    discountable = serializers.BooleanField(read_only=True)
    taxable = serializers.BooleanField(read_only=True)
    code = serializers.CharField(max_length=100)
    item_category = serializers.IntegerField(read_only=True)
    purchase_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    purchase_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    purchase_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    customer_order_pending_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class GetStockByBatchSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    purchase_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    purchase_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    customer_order_pending_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name']


class ItemLedgerSerializer(serializers.Serializer):
    qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    item_name = serializers.CharField(max_length=150, allow_null=True)
    item = serializers.IntegerField()
    supplier_customer_name = serializers.CharField(max_length=255, allow_null=True)
    supplier_customer = serializers.IntegerField(allow_null=True)
    batch_no = serializers.CharField(max_length=50)
    cost = serializers.IntegerField(allow_null=True)
    op_type = serializers.CharField(max_length=255, allow_null=True)


class RemainingItemCostSerialzier(serializers.Serializer):
    item = serializers.IntegerField()
    item_name = serializers.CharField(max_length=100)
    total_remaining_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_remaining_cost = serializers.DecimalField(max_digits=20, decimal_places=2)
