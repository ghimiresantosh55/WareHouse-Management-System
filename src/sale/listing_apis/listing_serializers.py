from rest_framework import serializers

from src.core_app.models import AdditionalChargeType, DiscountScheme, PaymentMode
from src.customer.models import Customer
from src.customer_order.models import OrderMaster
from src.item.models import Item, ItemCategory, PackingType
from src.sale.models import SaleMaster


class CustomerSaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no']
        read_only_fields = fields


class DiscoutnSchemeSaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = ['id', 'name', 'rate']
        read_only_fields = fields


class ItemCustomerOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'purchase_cost', 'sale_cost', 'name', 'discountable',
                  'taxable', 'tax_rate', 'code']
        read_only_fields = fields


class OrderMasterSaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMaster
        fields = ['id', 'order_no', 'status', 'customer',
                  'discount_scheme', 'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'delivery_date_ad', 'delivery_date_bs', 'delivery_location', 'grand_total', 'remarks'
                  ]
        read_only_fields = fields


class ItemCategorySaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'code']
        read_only_fields = fields


class PackingTypeSaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingType
        fields = ['id', 'name', 'short', 'name']
        read_only_fields = fields


class PaymentModeSaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id', 'name', 'remarks']
        read_only_fields = fields


class AdditionalChargeTypeSaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalChargeType
        fields = ['id', 'name']
        read_only_fields = fields


class SaleNoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no']
        read_only_fields = fields


class GetPackTypeDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=20)
    pack_type_code = serializers.IntegerField()
    batch_no = serializers.CharField(max_length=20)
    purchase_detail = serializers.IntegerField()
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=20)


class GetPackTypeByCodeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=20)
    location_code = serializers.CharField(max_length=20)
    batch_no = serializers.CharField(max_length=20)
    purchase_detail = serializers.IntegerField()
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=20)
