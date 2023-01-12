from decimal import Decimal

from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import SaleDetail, SaleMaster


class DispatchSerializer(serializers.Serializer):
    batch_no = serializers.CharField(max_length=8)
    sale_detail = serializers.PrimaryKeyRelatedField(queryset=SaleDetail.objects.filter(dispatched=False))
    qty = serializers.DecimalField(max_digits=8, decimal_places=2)
    location = serializers.CharField()

    def create(self, validated_data):

        if validated_data['sale_detail'].dispatched:
            raise serializers.ValidationError({"message": "This sale is already dispatched"})

        if Decimal(validated_data['qty']) != validated_data['sale_detail'].qty:
            raise serializers.ValidationError({"message": "quantity does not match"})

        batch_no_db = validated_data['sale_detail'].ref_purchase_detail.batch_no
        location_db_id = validated_data['sale_detail'].ref_purchase_detail.location.id

        if batch_no_db != validated_data['batch_no']:
            raise serializers.ValidationError({"message": "batch no does not match"})

        try:
            try:
                location_id = validated_data['location'].split("-")[1]
            except Exception:
                raise serializers.ValidationError({"message": "location format incorrect"})

            if int(location_db_id) != int(location_id):
                raise serializers.ValidationError({"message": "location id does not match"})
        except ValidationError as e:
            raise e

        validated_data['sale_detail'].dispatched = True
        validated_data['sale_detail'].save()

        return validated_data


class GetSaleDetailDispatchSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source="item.name")
    item_location = serializers.ReadOnlyField(source="ref_purchase_detail.location.get_path")
    batch_no = serializers.ReadOnlyField(source="ref_purchase_detail.batch_no")

    class Meta:
        model = SaleDetail
        exclude = ['sale_master']


class GetSaleForDispatchSerializer(serializers.ModelSerializer):
    sale_details = GetSaleDetailDispatchSerializer(many=True)

    class Meta:
        model = SaleMaster
        fields = "__all__"
