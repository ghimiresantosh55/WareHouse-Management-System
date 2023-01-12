from rest_framework import serializers

from src.supplier.models import Supplier
from src.purchase.models import PurchaseMaster, PurchaseDetail
from src.item.models import Item, ItemCategory


class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']
        read_only_fields = fields


class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'chalan_no', 'bill_no',
                  'bill_date_ad', 'bill_date_bs', 'due_date_ad', 'due_date_bs']
        read_only_fields = fields


class StockItemCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'code']


class ItemListStockSerializer(serializers.ModelSerializer):
    item_category = StockItemCategoryListSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'code', 'item_category', 'discountable', 'taxable', 'tax_rate', 'purchase_cost']
        read_only_fields = fields


class ItemListStockSubtractionListSerializer(serializers.ModelSerializer):
    item_category = StockItemCategoryListSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'item_category', 'code']


class BatchStockSubtractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDetail
        fields = ['id', 'batch_no', 'purchase_cost', 'sale_cost']
