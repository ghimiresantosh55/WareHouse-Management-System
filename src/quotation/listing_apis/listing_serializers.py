from decimal import Decimal

from rest_framework import serializers
from src.customer.models import Customer
from src.item.models import Item, ItemCategory


class CustomerQuotationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no']


class ItemCategoryQuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'code']


class ItemQuotationListSerializer(serializers.ModelSerializer):
    item_category = ItemCategoryQuotationSerializer()

    class Meta:
        model = Item
        fields = ['id', 'purchase_cost', 'sale_cost', 'name', 'discountable',
                  'taxable', 'tax_rate', 'code', 'item_category']


class RemainingItemQuotationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=255)
    item_category = serializers.IntegerField()
    remaining_qty = serializers.DecimalField(decimal_places=2, max_digits=9)
