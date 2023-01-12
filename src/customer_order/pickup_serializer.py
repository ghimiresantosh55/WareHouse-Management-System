from decimal import Decimal

from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.customer_order.models import OrderDetail, OrderMaster
from src.item_serialization.models import SalePackingTypeDetailCode


class VerifyOrderPickupSerializer(serializers.Serializer):
    order_master = serializers.PrimaryKeyRelatedField(
        queryset=OrderMaster.objects.filter(pick_verified=False, status=1, approved=True)
    )
    serial_nos = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    def create(self, validated_data):
        customer_order_serial_nos = SalePackingTypeDetailCode.objects.filter(
            sale_packing_type_code__customer_order_detail__order=validated_data['order_master']
        ).distinct("id").values_list("id", flat=True)
        request_serial_nos = list(validated_data['serial_nos'])
        verified_by = current_user.get_created_by(self.context)
        if list(customer_order_serial_nos).sort() == request_serial_nos.sort():
            order_master = validated_data['order_master']
            order_master.pick_verified = True
            order_master.verified_by = verified_by
            order_master.save()
        else:
            raise serializers.ValidationError(
                {'message': 'provided serial nos does not match'}
            )

        return validated_data


class OrderPickupSerializer(serializers.Serializer):
    order_detail = serializers.PrimaryKeyRelatedField(queryset=OrderDetail.objects.filter(picked=False,
                                                                                          order__approved=True))
    pack_type_detail_code_ids = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=SalePackingTypeDetailCode.objects.all()
    ))

    def to_representation(self, instance):
        quantize_places = Decimal(10) ** -2

        customer_order_detail_data = {
            "id": instance.id,
            "qty": str(Decimal(instance.qty).quantize(quantize_places)),
            "item_name": str(instance.item.name),
            "purchase_cost": str(Decimal(instance.purchase_cost).quantize(quantize_places)),
            "sale_cost": str(Decimal(instance.sale_cost).quantize(quantize_places)),
            "taxable": instance.taxable,
            "tax_rate": str(Decimal(instance.tax_rate).quantize(quantize_places)),
            "tax_amount": str(Decimal(instance.tax_amount).quantize(quantize_places)),
            "discountable": instance.discountable,
            "discount_rate": str(Decimal(instance.discount_rate).quantize(quantize_places)),
            "discount_amount": str(Decimal(instance.discount_amount).quantize(quantize_places)),
            "gross_amount": str(Decimal(instance.gross_amount).quantize(quantize_places)),
            "net_amount": str(Decimal(instance.net_amount).quantize(quantize_places)),
            "cancelled": instance.cancelled,
            "remarks": instance.remarks,
            "picked": instance.picked,
            "picked_by": instance.picked_by.id,
            "picked_by_name": instance.picked_by.user_name
        }

        return customer_order_detail_data

    def create(self, validated_data):

        if not validated_data['order_detail'].order.approved:
            raise serializers.ValidationError({"message": "This order has not been approved yet"})

        if validated_data['order_detail'].picked:
            raise serializers.ValidationError({"message": "This order is already picked"})

        if Decimal(len(validated_data['pack_type_detail_code_ids'])) != validated_data['order_detail'].qty:
            raise serializers.ValidationError({"message": "serial nos quantity does not match"})

        for pack_type_code in validated_data['pack_type_detail_code_ids']:
            if pack_type_code.sale_packing_type_code.customer_order_detail.id != validated_data['order_detail'].id:
                raise serializers.ValidationError({"message": "serial no does not match with customer order item"})

        validated_data['order_detail'].picked = True
        validated_data['order_detail'].picked_by = current_user.get_created_by(self.context)
        validated_data['order_detail'].save()
        return validated_data['order_detail']
