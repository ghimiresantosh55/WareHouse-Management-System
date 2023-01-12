from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from src.item_serialization.models import PackingTypeCode
from src.warehouse_location.models import Location
from .models import PurchaseOrderDetail, PurchaseDetail


class GetPackTypeCodeSerializer(serializers.ModelSerializer):
    location = serializers.ReadOnlyField(source='location.code', allow_null=True)

    class Meta:
        model = PackingTypeCode
        exclude = ['purchase_detail']


class GetLocationPurchaseOrderDetailsSerializer(serializers.ModelSerializer):
    po_pack_type_codes = GetPackTypeCodeSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    # item_category_name = serializer.ReadOnlyField(source='item_category.name', allow_null=True)
    packing_type = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)

    class Meta:
        model = PurchaseOrderDetail
        fields = ['id', 'po_pack_type_codes', 'item_name', 'packing_type']


class UpdateLocationPurchaseOrderDetailSerializer(serializers.Serializer):
    packing_type_code = serializers.CharField(max_length=20)
    location_code = serializers.CharField(max_length=50)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    purchase_order_detail_id = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        try:
            packing_type_code = PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True).get(
                code=validated_data['packing_type_code'])
            # if packing_type_code.location is not None: raise serializer.ValidationError({"message": f"this
            # packing_type : {packing_type_code.code} already have location"})

            try:
                location = Location.objects.get(code=validated_data['location_code'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError({"message": "this location does not exist"})
            if not location.is_leaf_node():
                raise serializers.ValidationError({"message": "location is not leaf node"})
            packing_type_code.location = location
            packing_type_code.save()
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"message": "packing type code does not match"})
        validated_data['id'] = packing_type_code
        validated_data['purchase_order_detail_id'] = packing_type_code.purchase_order_detail
        return validated_data


class POBulkLocationPackingTypeCodeSerializer(serializers.Serializer):
    pack_type_code = serializers.CharField(required=True, max_length=20)


class UpdateBulkLocationPurchaseOrderDetailSerializer(serializers.Serializer):
    pack_type_codes = POBulkLocationPackingTypeCodeSerializer(required=True, many=True)
    location_code = serializers.CharField(max_length=50)

    def create(self, validated_data):
        try:
            location = Location.objects.get(code=validated_data['location_code'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"message": "this location does not exist"})
        if not location.is_leaf_node():
            raise serializers.ValidationError({"message": "location is not leaf node"})

        for pack_code in validated_data['pack_type_codes']:
            try:
                packing_type_code = PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True).get(
                    code=pack_code['pack_type_code']
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError({"msg": "Pack Type Code with this id :"
                                                          " " + pack_code['pack_type_code'] + " does not exist"})
            packing_type_code.location = location
            packing_type_code.save()
        return validated_data


class UpdateLocationDirectPurchaseDetailSerializer(serializers.Serializer):
    packing_type_code = serializers.CharField(max_length=20)
    location_code = serializers.CharField(max_length=50)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    purchase_detail_id = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        try:
            packing_type_code = PackingTypeCode.objects.get(code=validated_data['packing_type_code'])
            try:
                location = Location.objects.get(code=validated_data['location_code'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError({"message": "this location does not exist"})
            if not location.is_leaf_node():
                raise serializers.ValidationError({"message": "location is not leaf node"})
            packing_type_code.location = location
            packing_type_code.save()
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"message": "packing type code does not match"})
        validated_data['id'] = packing_type_code
        validated_data['purchase_detail_id'] = packing_type_code.purchase_detail
        return validated_data


class UpdateBulkLocationDirectPurchaseDetailSerializer(serializers.Serializer):
    pack_type_codes = POBulkLocationPackingTypeCodeSerializer(required=True, many=True)
    location_code = serializers.CharField(max_length=50)

    def create(self, validated_data):
        try:
            location = Location.objects.get(code=validated_data['location_code'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"message": "this location does not exist"})
        if not location.is_leaf_node():
            raise serializers.ValidationError({"message": "location is not leaf node"})

        for pack_code in validated_data['pack_type_codes']:
            try:
                packing_type_code = PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True).get(
                    code=pack_code['pack_type_code']
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError({"msg": "Pack Type Code with this id :"
                                                          " " + pack_code['pack_type_code'] + " does not exist"})
            packing_type_code.location = location
            packing_type_code.save()
        return validated_data


class GetDirectPurchaseDetailPackTypeCodeSerializer(serializers.ModelSerializer):
    location = serializers.ReadOnlyField(source='location.code', allow_null=True)

    class Meta:
        model = PackingTypeCode
        exclude = ['purchase_detail']


class GetLocationDirectPurchaseDetailsSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = GetDirectPurchaseDetailPackTypeCodeSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    packing_type = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'pu_pack_type_codes', 'item_name', 'packing_type']
