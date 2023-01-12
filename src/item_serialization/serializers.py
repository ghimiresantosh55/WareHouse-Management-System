from rest_framework import serializers

from src.warehouse_location.models import Location
from .models import PackingTypeCode, PackingTypeDetailCode


class PackTypeCodeLocationSerializer(serializers.ModelSerializer):
    location_code = serializers.ReadOnlyField(source='location.code')

    class Meta:
        model = PackingTypeCode
        fields = ['id', 'code', 'location', 'location_code']


class UpdatePackTypeLocationSerializer(serializers.Serializer):
    pack_type_code_id = serializers.PrimaryKeyRelatedField(
        queryset=PackingTypeCode.objects.all()
    )
    location_code = serializers.CharField(
        max_length=40
    )

    def create(self, validated_data):
        try:
            location = Location.objects.get(code=validated_data['location_code'])
        except Location.DoesNotExist:
            raise serializers.ValidationError({'message': 'location does not exist'})
        pack_type_detail_code = validated_data['pack_type_code_id']
        pack_type_detail_code.location = location
        pack_type_detail_code.save()
        return validated_data


class PackTypeDetailCodeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        fields = ['id', 'code']
        read_only_fields = fields


class PackTypeCodeInfoSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = PackTypeDetailCodeInfoSerializer(many=True, read_only=True)
    item_name = serializers.ReadOnlyField(source='purchase_detail.item.name', allow_null=True)
    location_code = serializers.ReadOnlyField(source='location.code', allow_null=True)
    batch_no = serializers.ReadOnlyField(source='purchase_detail.batch_no', allow_null=True)
    supplier_name = serializers.ReadOnlyField(source='purchase_detail.purchase.supplier.name', allow_null=True)

    class Meta:
        model = PackingTypeCode
        fields = ['id', 'code', 'location_code', 'item_name', 'batch_no', 'supplier_name', 'pack_type_detail_codes']
        read_only_fields = fields


class PackCodeDetailInfoSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(
        source="pack_type_code.purchase_detail.item.name",
        allow_null=True)
    item_category_name = serializers.ReadOnlyField(
        source="pack_type_code.purchase_detail.item_category.name",
        allow_null=True
    )
    batch_no = serializers.ReadOnlyField(
        source="pack_type_code.purchase_detail.batch_no",
        allow_null=True
    )
    pack_type_code = serializers.ReadOnlyField(source='pack_type_code.code', allow_null=True)
    location_code = serializers.ReadOnlyField(source='pack_type_code.location.code', allow_null=True)

    class Meta:
        model = PackingTypeDetailCode
        fields = ['id', 'code', 'item_name', 'item_category_name', 'batch_no', 'pack_type_code', 'location_code']
