from rest_framework import serializers


class GetStockByBatchListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    purchase_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sale_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    purchase_return_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    customer_order_pending_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class GetPackTypeDetailByBatchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=20)
    pack_type_code = serializers.IntegerField()
    batch_no = serializers.CharField(max_length=20)
    purchase_detail = serializers.IntegerField()
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=20)


class GetPackTypeByBatchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=20)
    location_code = serializers.CharField(max_length=20)
    batch_no = serializers.CharField(max_length=20)
    purchase_detail = serializers.IntegerField()
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=20)
    qty = serializers.DecimalField(max_digits=12, decimal_places=2)
