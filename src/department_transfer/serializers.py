from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .department_transfer_unique_id_generator import generate_department_transfer_no
from .models import DepartmentTransferMaster, DepartmentTransferDetail
from src.custom_lib.functions.current_user import get_created_by
from ..item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from ..item_serialization.services import pack_and_serial_info


class SaveDepartmentTransferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentTransferDetail
        exclude = ['ref_department_transfer_detail']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'department_transfer_master']
        extra_kwargs = {
            'ref_purchase_detail': {'required': True}
        }


class SaveDepartmentTransferMasterSerializer(serializers.ModelSerializer):
    department_transfer_details = SaveDepartmentTransferDetailSerializer(many=True, required=True)

    class Meta:
        model = DepartmentTransferMaster
        exclude = ['ref_department_transfer_master']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'transfer_no', 'transfer_type']

    def create(self, validated_data):
        date_now = timezone.now()
        created_by = get_created_by(self.context)
        department_transfer_details = validated_data.pop("department_transfer_details")
        department_transfer_master = DepartmentTransferMaster.objects.create(
            **validated_data, created_date_ad=date_now,
            created_by=created_by, transfer_no=generate_department_transfer_no(1), transfer_type=1
        )

        for department_transfer_detail in department_transfer_details:
            DepartmentTransferDetail.objects.create(
                **department_transfer_detail, created_by=created_by, created_date_ad=date_now,
                department_transfer_master=department_transfer_master
            )

        return department_transfer_master

    def validate(self, attrs):
        return super(SaveDepartmentTransferMasterSerializer, self).validate(attrs)


class DepartmentTransferPackingTypeDetailCodeListSerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source='packing_type_detail_code.code')

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'code']
        read_only_fields = fields


class DepartmentTransferPackingTypeCodeSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = DepartmentTransferPackingTypeDetailCodeListSerializer(many=True)
    code = serializers.ReadOnlyField(source='packing_type_code.code', allow_null=True)
    location_code = serializers.ReadOnlyField(source='packing_type_code.location.code', allow_null=True)
    location = serializers.ReadOnlyField(source='packing_type_code.location.id', allow_null=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'location_code', 'location', 'code', 'qty',
                  'sale_detail', 'packing_type_code', 'sale_packing_type_detail_code']


class DepartmentTransferDetailListSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    item_unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    batch_no = serializers.ReadOnlyField(source='ref_purchase_detail.batch_no', allow_null=True)
    department_transfer_packing_types = DepartmentTransferPackingTypeCodeSerializer(many=True)
    item_is_serializable = serializers.ReadOnlyField(source="ref_purchase_detail.item.is_serializable", allow_null=True)
    picked_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = DepartmentTransferDetail
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'department_transfer_master']


class DepartmentTransferDetailSummarySerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    item_unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    batch_no = serializers.ReadOnlyField(source='ref_purchase_detail.batch_no', allow_null=True)

    class Meta:
        model = DepartmentTransferDetail
        exclude = ['ref_department_transfer_detail']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'department_transfer_master']


class DepartmentTransferMasterSummarySerializer(serializers.ModelSerializer):
    department_transfer_details = DepartmentTransferDetailSummarySerializer(many=True, required=True)
    from_department = serializers.SerializerMethodField()
    to_department = serializers.SerializerMethodField()
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    received_by_user_name = serializers.ReadOnlyField(source='received_by.user_name', allow_null=True)
    approved_by_user_name = serializers.ReadOnlyField(source='approved_by.user_name', allow_null=True)

    class Meta:
        model = DepartmentTransferMaster
        exclude = ['ref_department_transfer_master']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'transfer_no', 'transfer_type']

    def get_from_department(self, instance):
        return {
            "id": instance.from_department.id,
            "name": instance.from_department.name,
        }

    def get_to_department(self, instance):
        return {
            "id": instance.to_department.id,
            "name": instance.to_department.name,
        }


class DepartmentTransferMasterListSerializer(serializers.ModelSerializer):
    from_department = serializers.SerializerMethodField()
    to_department = serializers.SerializerMethodField()
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    received_by_user_name = serializers.ReadOnlyField(source='received_by.user_name', allow_null=True)
    approved_by_user_name = serializers.ReadOnlyField(source='approved_by.user_name', allow_null=True)

    class Meta:
        model = DepartmentTransferMaster
        exclude = ['ref_department_transfer_master']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'transfer_no', 'transfer_type']

    def get_from_department(self, instance):
        return {
            "id": instance.from_department.id,
            "name": instance.from_department.name,
        }

    def get_to_department(self, instance):
        return {
            "id": instance.to_department.id,
            "name": instance.to_department.name,
        }


class CancelDepartmentTransferDetailSerializer(serializers.Serializer):
    department_transfer_detail = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentTransferDetail.objects.filter(
            is_cancelled=False, department_transfer_master__is_approved=False
        ))
    is_cancelled = serializers.BooleanField()

    def create(self, validated_data):
        department_transfer_detail = validated_data['department_transfer_detail']
        department_transfer_detail.is_cancelled = True
        department_transfer_detail.save()
        department_transfer_master = department_transfer_detail.department_transfer_master
        department_transfer_master.grand_total = department_transfer_master.grand_total - department_transfer_detail.net_amount
        department_transfer_master.save()
        return validated_data


class CancelDepartmentTransferMasterSerializer(serializers.Serializer):
    department_transfer_master = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentTransferMaster.objects.filter(
            is_cancelled=False, is_approved=False, is_received=False
        ))
    is_cancelled = serializers.BooleanField()

    def create(self, validated_data):
        department_transfer_master = validated_data['department_transfer_master']
        department_transfer_master.is_cancelled = True
        department_transfer_master.save()
        department_transfer_details = DepartmentTransferDetail.objects.filter(
            department_transfer_master=department_transfer_master
        )
        for department_transfer_detail in department_transfer_details:
            department_transfer_detail.is_cancelled = True
            department_transfer_detail.save()

        return validated_data


class UpdateDepartmentTransferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentTransferDetail
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class UpdateDepartmentTransferMasterSerializer(serializers.ModelSerializer):
    department_transfer_details = UpdateDepartmentTransferDetailSerializer(many=True, required=False)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')

    class Meta:
        model = DepartmentTransferMaster
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def update(self, instance, validated_data):
        current_date = timezone.now()
        try:
            department_transfer_details = validated_data.pop('department_transfer_details')
        except KeyError:
            department_transfer_details = []

        created_by = self.context.get('request').user
        instance.grand_total = validated_data.get("grand_total", instance.grand_total)
        instance.save()

        for department_transfer_detail in department_transfer_details:
            DepartmentTransferDetail.objects.create(
                **department_transfer_detail, department_transfer_master=instance,
                created_by=created_by,
                created_date_ad=current_date
            )

        return instance


class ApproveDepartmentTransferMasterSerializer(serializers.Serializer):
    department_transfer_master = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentTransferMaster.objects.filter(
            is_cancelled=False, is_approved=False, is_received=False
        ))
    is_approved = serializers.BooleanField()

    def create(self, validated_data):
        department_transfer_master = validated_data['department_transfer_master']
        department_transfer_master.is_approved = True
        department_transfer_master.approved_by = self.context.get("request").user
        department_transfer_master.save()
        department_transfer_details = DepartmentTransferDetail.objects.filter(
            department_transfer_master=department_transfer_master, is_cancelled=False
        )
        if department_transfer_details.count() <= 0:
            raise serializers.ValidationError(
                {'error': "no details found for this master"}
            )

        return validated_data


class PickupDepartmentTransferPackingTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code']


class PickupDepartmentTransferPackingTypesSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = PickupDepartmentTransferPackingTypeDetailsSerializer(many=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'packing_type_code', 'sale_packing_type_detail_code', 'qty']
        extra_kwargs = {
            'qty': {'required': True}
        }


class PickupDepartmentTransferDetailSerializer(serializers.Serializer):
    department_transfer_detail = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentTransferDetail.objects.filter(
            is_cancelled=False, is_picked=False, department_transfer_master__is_approved=True
        )
    )
    department_transfer_packing_types = PickupDepartmentTransferPackingTypesSerializer(many=True, required=True)

    def to_representation(self, instance):

        department_transfer_detail = DepartmentTransferDetail.objects.get(id=instance['department_transfer_detail'].id)

        quantize_places = Decimal(10) ** -2

        department_transfer_detail_data = {
            "id": department_transfer_detail.id,
            "qty": str(Decimal(department_transfer_detail.qty).quantize(quantize_places)),
            "item_name": str(department_transfer_detail.item.name),
            "purchase_cost": str(Decimal(department_transfer_detail.purchase_cost).quantize(quantize_places)),
            "net_amount": str(Decimal(department_transfer_detail.net_amount).quantize(quantize_places)),
            "is_cancelled": department_transfer_detail.is_cancelled,
            "remarks": department_transfer_detail.remarks,
            "is_picked": department_transfer_detail.is_picked,
            "picked_by_user_name": department_transfer_detail.picked_by.user_name
        }

        return department_transfer_detail_data

    def create(self, validated_data):
        department_transfer_detail = validated_data['department_transfer_detail']
        is_serializable = department_transfer_detail.ref_purchase_detail.item.is_serializable
        department_transfer_detail.is_picked = True
        department_transfer_detail.picked_by = self.context.get("request").user
        department_transfer_detail.save()
        department_transfer_packing_types = validated_data['department_transfer_packing_types']
        transfer_qty = department_transfer_detail.qty
        serial_no_count = 0

        # update is_picked status for master
        department_transfer_master = department_transfer_detail.department_transfer_master
        if not DepartmentTransferDetail.objects.filter(department_transfer_master=department_transfer_master).exists():
            department_transfer_master.is_picked = True
            department_transfer_master.save()
        for department_transfer_packing_type in department_transfer_packing_types:
            sale_pack_type_details = department_transfer_packing_type['sale_packing_type_detail_code']
            sale_pack_type_db = SalePackingTypeCode.objects.create(
                packing_type_code=department_transfer_packing_type['packing_type_code'],
                department_transfer_detail=department_transfer_detail,
                qty=department_transfer_packing_type['qty']
            )
            for sale_pack_type_detail in sale_pack_type_details:
                SalePackingTypeDetailCode.objects.create(
                    packing_type_detail_code=sale_pack_type_detail['packing_type_detail_code'],
                    sale_packing_type_code=sale_pack_type_db
                )
                serial_no_count += 1
        if is_serializable:
            if transfer_qty != serial_no_count:
                raise serializers.ValidationError(
                    {"error": f"order qty {transfer_qty} is not equal to serial_nos scanned {serial_no_count}"})
        return validated_data

    def validate(self, attrs):
        department_transfer_packing_types = attrs['department_transfer_packing_types']
        for department_transfer_packing_type in department_transfer_packing_types:
            packing_type_code = department_transfer_packing_type['packing_type_code']
            if attrs['department_transfer_detail'].item.is_serializable is True:
                available_pack = pack_and_serial_info.find_available_serial_nos(packing_type_code.id)
                if not available_pack.exists():
                    raise serializers.ValidationError({"message": f"{packing_type_code.code} is not available"})
                sale_pack_type_details = department_transfer_packing_type['sale_packing_type_detail_code']
                for sale_pack_type_detail in sale_pack_type_details:
                    serial_no_code = sale_pack_type_detail['packing_type_detail_code']
                    available_serial_no = pack_and_serial_info.find_available_serial_no_id(serial_no_code.id)
                    if not available_serial_no:
                        raise serializers.ValidationError({"message": f"{serial_no_code.code} is not available"})
            else:
                pack = pack_and_serial_info.available_pack_qty_non_serializable(
                    department_transfer_packing_type['packing_type_code'].id)
                remaining_qty = pack['qty'] - pack['sold_qty'] + pack['return_qty']
                if department_transfer_packing_type['qty'] > remaining_qty:
                    raise serializers.ValidationError(
                        {
                            "error": f"packet qty {department_transfer_packing_type['qty']} "
                                     f"more than remaining qty of packet {remaining_qty}"
                        }
                    )

        return super(PickupDepartmentTransferDetailSerializer, self).validate(attrs)
