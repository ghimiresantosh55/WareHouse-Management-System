from rest_framework import serializers

from src.department.models import Department
from src.item.models import Item


class DepartmentTransferDepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class DepartmentTransferItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    item_category = serializers.IntegerField()
    purchase_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    item_highest_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    name = serializers.CharField(max_length=250)
    code = serializers.CharField(max_length=250)
    tax_rate = serializers.DecimalField(max_digits=12, decimal_places=2)
    sale_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    remaining_qty = serializers.DecimalField(max_digits=12, decimal_places=2)
    discountable = serializers.BooleanField()
    taxable = serializers.BooleanField()


class GetDepartmentStockByBatchListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    purchase_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    purchase_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    customer_order_pending_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class DepartmentTransferPackTypeCodesByBatchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=20)
    location_code = serializers.CharField(max_length=20)
    batch_no = serializers.CharField(max_length=20)
    purchase_detail = serializers.IntegerField()
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=20)
    qty = serializers.DecimalField(max_digits=12, decimal_places=2)


class DepartmentTransferPackTypeDetailListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=20)
    pack_type_code = serializers.IntegerField()
    batch_no = serializers.CharField(max_length=20)
    purchase_detail = serializers.IntegerField()
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=20)
