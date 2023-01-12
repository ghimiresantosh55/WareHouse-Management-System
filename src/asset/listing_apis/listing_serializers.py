from rest_framework import serializers

from src.item.models import Item
from src.item_serialization.models import PackingTypeDetailCode


class AssetSerialNoInfoListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(max_length=100, read_only=True)
    item_name = serializers.CharField(max_length=100, read_only=True)
    purchase_no = serializers.CharField(max_length=25, read_only=True)
    bill_no = serializers.CharField(max_length=100, read_only=True)
    item_category_name = serializers.CharField(max_length=100, read_only=True)

    class Meta:
        model = PackingTypeDetailCode
        fields = ["id", "code", "supplier_name",
                  "item_name", "purchase_no", "bill_no", "item_category_name"]
        extra_kwargs = {
            "code": {"read_only": True}
        }
        red_only_fields = fields


class AssetItemLIstSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'purchase_cost']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type']


class PackTypeDetailCodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        fields = "__all__"
