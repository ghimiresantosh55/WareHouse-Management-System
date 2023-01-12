from rest_framework import serializers

from src.core_app.models import AdditionalChargeType, Country, DiscountScheme, PaymentMode, Currency
from src.department.models import Department
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail
from src.purchase.models import PurchaseDocumentType, PurchaseMaster, PurchaseOrderMaster
from src.supplier.models import Supplier


class PurchaseDiscontSchemeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = ["id", "name", "rate"]


class PurchaseSupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']


class PurchaseCountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class PurchaseCurrencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class PurchaseItemCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'code']


class PurchaseItemListSerializer(serializers.ModelSerializer):
    item_category = PurchaseItemCategoryListSerializer(read_only=True)
    unit = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'name', 'code', 'item_category', 'discountable', 'taxable',
                  'tax_rate', 'purchase_cost', 'is_serializable', 'unit']

    def get_unit(self, instance):
        return {
            "id": instance.unit.id,
            "name": instance.unit.name,
            "short_form": instance.unit.short_form,
            "display_order": instance.unit.display_order
        }


class PurchasePackingTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingType
        fields = ['id', 'name', 'short_name']


class PurchasePackingTypeDetailListSerializer(serializers.ModelSerializer):
    packing_type = PurchasePackingTypeListSerializer(read_only=True)

    class Meta:
        model = PackingTypeDetail
        fields = ['id', 'item', 'packing_type', 'pack_qty']


# pay mode , additionl charge, doc type
class PurchasePurchaseDocumentTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDocumentType
        fields = ['id', 'name']


class PurchasePaymentModeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id', 'name']


class PurchaseAdditionalChargeTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalChargeType
        fields = ['id', 'name']


class PurchaseNoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no']


class PurchaseOrderNoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no']


class PurchaseDepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']
