import decimal

from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.department_transfer.models import DepartmentTransferMaster, DepartmentTransferDetail
from src.item_serialization.models import PackingTypeDetailCode, PackingTypeCode
from src.item_serialization.unique_item_serials import generate_packtype_serial, packing_type_detail_code_list
from src.purchase.models import PurchaseDetail, PurchaseMaster
from src.purchase.purchase_unique_id_generator import generate_purchase_no

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


class ReceiveDepartmentTransferPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        exclude = ["pack_type_code"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class ReceiveDepartmentTransferPackingTypeCodeSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = ReceiveDepartmentTransferPackingTypeDetailCodeSerializer(many=True, required=False)
    pack_no = serializers.IntegerField(write_only=True)

    class Meta:
        model = PackingTypeCode
        exclude = ["purchase_order_detail", "purchase_detail"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'code']
        extra_kwargs = {
            'pack_no': {'write_only': True}
        }


# purchase order detail serializer for Write Only purchase_order_view
class ReceiveDepartmentTransferDetailSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = ReceiveDepartmentTransferPackingTypeCodeSerializer(many=True)
    pack_qty = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    sale_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    ref_department_transfer_detail = serializers.IntegerField(required=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['purchase']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'item_category', 'pack_qty']


# purchase order master nested serializer for Write Only purchase_order_view
class ReceiveDepartmentTransferMasterSerializer(serializers.ModelSerializer):
    purchase_details = ReceiveDepartmentTransferDetailSerializer(many=True)

    ref_department_transfer_master = serializers.IntegerField(required=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        validated_data['purchase_no'] = generate_purchase_no(6)
        date_now = timezone.now()
        purchase_details = validated_data.pop('purchase_details')
        purchase_master = PurchaseMaster.objects.create(
            **validated_data, created_date_ad=date_now
        )
        for purchase_detail in purchase_details:
            pack_type_codes = purchase_detail.pop('pu_pack_type_codes')
            purchase_detail_for_serial = PurchaseDetail.objects.create(
                **purchase_detail, pack_qty=purchase_detail['packing_type_detail'].pack_qty,
                item_category=purchase_detail['item'].item_category,
                purchase=purchase_master, created_by=validated_data['created_by'], created_date_ad=date_now
            )

            len_of_pack_type_code = len(pack_type_codes)
            ref_len_pack_type_code = int(
                purchase_detail['qty'] / purchase_detail['packing_type_detail'].pack_qty)
            if len_of_pack_type_code != ref_len_pack_type_code:
                raise serializers.ValidationError({"message": "pack type codes not enough"})
            for pack_type_code in pack_type_codes:
                pack_type_detail_codes = []
                if purchase_detail['item'].is_serializable is True:
                    pack_type_detail_codes = pack_type_code.pop('pack_type_detail_codes')

                code = generate_packtype_serial()
                pack_type = PackingTypeCode.objects.create(
                    code=code,
                    purchase_detail=purchase_detail_for_serial,
                    created_by=validated_data['created_by'],
                    created_date_ad=date_now,
                    qty=purchase_detail['packing_type_detail'].pack_qty
                )
                if purchase_detail['item'].is_serializable is True:
                    if pack_type_detail_codes:
                        if len(pack_type_detail_codes) != int(purchase_detail['packing_type_detail'].pack_qty):
                            raise serializers.ValidationError(
                                {"message": "packing type detail codes count does nto match"})
                        for pack_type_detail_code in pack_type_detail_codes:
                            if PackingTypeDetailCode.objects.filter(code=pack_type_detail_code['code']).exists():
                                raise serializers.ValidationError(
                                    {'serial_no': f'{pack_type_detail_code["code"]} already exists'})
                            PackingTypeDetailCode.objects.create(
                                code=pack_type_detail_code['code'],
                                pack_type_code=pack_type,
                                created_by=validated_data['created_by'],
                                created_date_ad=date_now
                            )
                    else:
                        pack_qty = int(purchase_detail['packing_type_detail'].pack_qty)

                        pack_type_detail_codes_data = packing_type_detail_code_list(pack_qty=pack_qty,
                                                                                    pack_type_code=pack_type.id,
                                                                                    created_by=validated_data[
                                                                                        'created_by'].id,
                                                                                    created_date_ad=date_now)
                        PackingTypeDetailCode.objects.bulk_create(
                            pack_type_detail_codes_data
                        )
        return purchase_master

    def validate(self, attrs):
        try:
            DepartmentTransferMaster.objects.filter(
                is_cancelled=False, is_picked=True, is_approved=True
            ).get(id=attrs['ref_department_transfer_master'])
        except DepartmentTransferMaster.DoesNotExist:
            raise serializers.ValidationError(
                {"ref_department_transfer_master": "Does not exist"}
            )
        grand_total = decimal.Decimal("0.00")
        for purchase_detail in attrs['purchase_details']:
            try:
                DepartmentTransferDetail.objects.filter(
                    is_picked=True, is_cancelled=False
                ).get(id=purchase_detail['ref_department_transfer_detail'])
            except DepartmentTransferDetail.DoesNotExist:
                raise serializers.ValidationError(
                    {'ref_department_transfer_detail': 'does not exist'}
                )
            grand_total = grand_total + purchase_detail['net_amount']

        if grand_total != attrs['grand_total']:
            raise serializers.ValidationError(
                {'grand_total': 'grand_total calculation does not match'}
            )
        return super(ReceiveDepartmentTransferMasterSerializer, self).validate(attrs)
