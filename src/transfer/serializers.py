from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions.current_user import get_created_by
from .models import TransferMaster, TransferDetail, TransferOrderMaster, TransferOrderDetail
from .transfer_helper import save_transfer_data_to_branch
from ..core_app.models import FiscalSessionAD, FiscalSessionBS
from ..custom_lib.functions import current_user
from ..custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from ..item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode


class SaveTransferDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale_master.sale_no')
    pack_qty = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), required=False)

    class Meta:
        model = TransferDetail
        exclude = ['transfer_master']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveTransferMasterSerializer(serializers.ModelSerializer):
    transfer_details = SaveTransferDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')

    class Meta:
        model = TransferMaster
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by',
                            'fiscal_session_ad', 'fiscal_session_bs']

    def create(self, validated_data):
        validated_data['created_by'] = get_created_by(self.context)
        date_now = timezone.now()
        transfer_details = validated_data.pop('transfer_details')
        if not transfer_details:
            raise serializers.ValidationError("Please provide at least one transfer detail")

        current_fiscal_session_short_ad = get_fiscal_year_code_ad()
        current_fiscal_session_short_bs = get_fiscal_year_code_bs()

        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)
        except Exception as e:
            raise serializers.ValidationError("fiscal session does not match")

        transfer_master = TransferMaster.objects.create(
            **validated_data, created_date_ad=date_now,
            fiscal_session_ad=fiscal_session_ad,
            fiscal_session_bs=fiscal_session_bs
        )
        for transfer_detail in transfer_details:
            TransferDetail.objects.create(**transfer_detail, transfer_master=transfer_master,
                                          created_by=validated_data['created_by'],
                                          created_date_ad=date_now)

        return transfer_master


class TransferMasterListSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    is_picked = serializers.SerializerMethodField()

    class Meta:
        model = TransferMaster
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by',
                            'fiscal_session_ad', 'fiscal_session_bs']

    def get_is_picked(self, instance):
        if instance.transfer_details.filter(is_picked=False,
                                            cancelled=False).exists():
            return False
        else:
            return True


class TransferPackTypeDetailCodeSummarySerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source="packing_type_detail_code.code", allow_null=True)

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'code']


class TransferPackTypeCodeSummarySerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = TransferPackTypeDetailCodeSummarySerializer(many=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'sale_packing_type_detail_code']


class TransferDetailListSerializer(serializers.ModelSerializer):
    batch_no = serializers.ReadOnlyField(source="ref_purchase_detail.batch_no", allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale_master.sale_no')
    pack_qty = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), required=False)
    transfer_packing_types = TransferPackTypeCodeSummarySerializer(many=True, read_only=True)

    class Meta:
        model = TransferDetail
        exclude = ['transfer_master']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class TransferSummarySerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    transfer_details = TransferDetailListSerializer(many=True)
    is_picked = serializers.SerializerMethodField()

    class Meta:
        model = TransferMaster
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by',
                            'fiscal_session_ad', 'fiscal_session_bs']

    def get_is_picked(self, instance):
        if instance.transfer_details.filter(is_picked=False).exists():
            return False
        else:
            return True


class SaveTransferOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferOrderDetail
        exclude = ['transfer_order_master']
        read_only_fields = ['id', 'created_date_ad', 'created_date_bs', 'created_by']


class SaveTransferOrderMasterSerializer(serializers.ModelSerializer):
    transfer_order_details = SaveTransferOrderDetailSerializer(many=True)

    class Meta:
        model = TransferOrderMaster
        fields = "__all__"
        read_only_fields = ['id', 'created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        created_by_user = get_created_by(self.context)
        date_now = timezone.now()

        transfer_order_details = validated_data.pop("transfer_order_details")

        transfer_order_master = TransferOrderMaster.objects.create(
            **validated_data,
            created_by=created_by_user,
            created_date_ad=date_now
        )
        for transfer_order_detail in transfer_order_details:
            TransferOrderDetail.objects.create(
                **transfer_order_detail,
                created_by=created_by_user,
                created_date_ad=date_now,
                transfer_order_master=transfer_order_master
            )

        return transfer_order_master


class TransferOrderMasterListSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')

    class Meta:
        model = TransferOrderMaster
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class TransferOrderDetailListSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    pack_qty = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), required=False)

    class Meta:
        model = TransferOrderDetail
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class TransferPackTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code']


class TransferPackTypeCodeSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = TransferPackTypeDetailCodeSerializer(many=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'packing_type_code', 'sale_packing_type_detail_code']


class PickupTransferDetailSerializer(serializers.Serializer):
    transfer_detail = serializers.PrimaryKeyRelatedField(
        queryset=TransferDetail.objects.filter(is_picked=False, cancelled=False), write_only=True
    )
    transfer_packing_types = TransferPackTypeCodeSerializer(many=True, write_only=True)
    id = serializers.IntegerField(read_only=True)
    item_name = serializers.CharField(max_length=200, read_only=True)
    batch_no = serializers.CharField(max_length=200, read_only=True)
    cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_rate = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_rate = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    cancelled = serializers.BooleanField(read_only=True)
    is_picked = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        # save sale packing type codes
        transfer_detail_db = validated_data["transfer_detail"]
        transfer_detail_db.is_picked = True
        transfer_detail_db.save()
        transfer_packing_types = validated_data.pop("transfer_packing_types")
        for pack in transfer_packing_types:
            sale_packing_type_detail_code = pack.pop('sale_packing_type_detail_code')
            sale_packing_type_code_db = SalePackingTypeCode.objects.create(
                **pack,
                transfer_detail=transfer_detail_db
            )
            for sale_pack_detail in sale_packing_type_detail_code:
                SalePackingTypeDetailCode.objects.create(
                    **sale_pack_detail,
                    sale_packing_type_code=sale_packing_type_code_db
                )
        validated_data['id'] = transfer_detail_db.id
        validated_data['item_name'] = transfer_detail_db.item.name
        validated_data['batch_no'] = transfer_detail_db.ref_purchase_detail.batch_no
        validated_data['cost'] = transfer_detail_db.cost
        validated_data['qty'] = transfer_detail_db.qty
        validated_data['discount_rate'] = transfer_detail_db.discount_rate
        validated_data['discount_amount'] = transfer_detail_db.discount_amount
        validated_data['tax_rate'] = transfer_detail_db.tax_rate
        validated_data['tax_amount'] = transfer_detail_db.tax_amount
        validated_data['gross_amount'] = transfer_detail_db.gross_amount
        validated_data['net_amount'] = transfer_detail_db.net_amount
        validated_data['cancelled'] = transfer_detail_db.cancelled
        validated_data['is_picked'] = transfer_detail_db.is_picked
        return validated_data


class SendTransferSerializer(serializers.Serializer):
    transfer_master = serializers.PrimaryKeyRelatedField(
        queryset=TransferMaster.objects.filter(is_transferred=False, cancelled=False)
    )
    message = serializers.CharField(max_length=100, read_only=True)

    def create(self, validated_data):
        return validated_data


class CancelTransferDetailSerializer(serializers.Serializer):
    transfer_detail = serializers.PrimaryKeyRelatedField(
        queryset=TransferDetail.objects.filter(transfer_master__is_transferred=False),
        write_only=True
    )
    id = serializers.IntegerField(read_only=True)
    item_name = serializers.CharField(max_length=200, read_only=True)
    batch_no = serializers.CharField(max_length=200, read_only=True)
    cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    qty = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_rate = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_rate = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    cancelled = serializers.BooleanField(read_only=True)

    def create(self, validated_data):

        transfer_detail = validated_data["transfer_detail"]
        # update transfer master
        transfer_master = validated_data["transfer_detail"].transfer_master
        transfer_master.sub_total = transfer_master.sub_total - transfer_detail.gross_amount
        if transfer_detail.discountable:
            transfer_master.total_discountable_amount = transfer_master.total_discountable_amount - transfer_detail.gross_amount
        if transfer_detail.taxable:
            transfer_master.total_taxable_amount = transfer_master.total_taxable_amount - (
                    transfer_detail.gross_amount - transfer_detail.discount_amount
            )
        else:
            transfer_master.total_non_taxable_amount = transfer_master.total_non_taxable_amount - (
                    transfer_detail.gross_amount - transfer_detail.discount_amount
            )
        transfer_master.total_discount = transfer_master.total_discount - transfer_detail.discount_amount
        transfer_master.total_tax = transfer_master.total_tax - transfer_detail.tax_amount
        transfer_master.grand_total = transfer_master.grand_total - transfer_detail.net_amount
        transfer_master.save()
        #  update transfer detail
        transfer_detail.pack_qty = 0
        transfer_detail.tax_amount = 0
        transfer_detail.discount_rate = 0
        transfer_detail.discount_amount = 0
        transfer_detail.gross_amount = 0
        transfer_detail.net_amount = 0
        transfer_detail.cancelled = True
        transfer_detail.save()

        # delete packets and serial nos
        sale_packing_type_codes = SalePackingTypeCode.objects.filter(transfer_detail=transfer_detail)
        for sale_packing_type_code in sale_packing_type_codes:
            sale_packing_type_code.sale_packing_type_detail_code.all().delete()
        sale_packing_type_codes.delete()
        # validated_data['message'] = "transfer cancelled successfully"
        validated_data['id'] = transfer_detail.id
        validated_data['item_name'] = transfer_detail.item.name
        validated_data['batch_no'] = transfer_detail.ref_purchase_detail.batch_no
        validated_data['cost'] = transfer_detail.cost
        validated_data['qty'] = transfer_detail.qty
        validated_data['discount_rate'] = transfer_detail.discount_rate
        validated_data['discount_amount'] = transfer_detail.discount_amount
        validated_data['tax_rate'] = transfer_detail.tax_rate
        validated_data['tax_amount'] = transfer_detail.tax_amount
        validated_data['gross_amount'] = transfer_detail.gross_amount
        validated_data['net_amount'] = transfer_detail.net_amount
        validated_data['cancelled'] = transfer_detail.cancelled

        return validated_data

    def validate(self, attrs):
        return super(CancelTransferDetailSerializer, self).validate(attrs)


class CancelTransferMasterSerializer(serializers.Serializer):
    transfer_master = serializers.PrimaryKeyRelatedField(
        queryset=TransferMaster.objects.filter(is_transferred=False)
    )
    message = serializers.CharField(max_length=100, read_only=True)

    def create(self, validated_data):
        transfer_master = validated_data['transfer_master']
        transfer_master.cancelled = True
        transfer_master.discount_rate = 0
        transfer_master.total_discountable_amount = 0
        transfer_master.total_taxable_amount = 0
        transfer_master.total_non_taxable_amount = 0
        transfer_master.total_tax = 0
        transfer_master.grand_total = 0
        transfer_master.sub_total = 0
        transfer_master.save()
        transfer_details = TransferDetail.objects.filter(transfer_master=transfer_master)
        for transfer_detail in transfer_details:
            #  update transfer detail
            transfer_detail.pack_qty = 0
            transfer_detail.tax_amount = 0
            transfer_detail.discount_rate = 0
            transfer_detail.discount_amount = 0
            transfer_detail.gross_amount = 0
            transfer_detail.net_amount = 0
            transfer_detail.cancelled = True
            transfer_detail.save()

            # delete packets and serial nos
            sale_packing_type_codes = SalePackingTypeCode.objects.filter(transfer_detail=transfer_detail)
            for sale_packing_type_code in sale_packing_type_codes:
                sale_packing_type_code.sale_packing_type_detail_code.all().delete()
            sale_packing_type_codes.delete()
        validated_data['message'] = "transfer master successfully cancelled"
        return validated_data


class TransferToBranchPackingTypeDetailSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)


class TransferToBranchPackingTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sale_packing_type_detail_code = TransferToBranchPackingTypeDetailSerializer(many=True)


class TransferToBranchDetailSerializer(serializers.Serializer):
    item = serializers.IntegerField()
    item_category = serializers.IntegerField()
    pack_qty = serializers.IntegerField()
    cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    qty = serializers.IntegerField()
    gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transfer_packing_types = TransferToBranchPackingTypeSerializer(many=True)


class TransferToBranchSerializer(serializers.Serializer):
    transfer_master = serializers.PrimaryKeyRelatedField(
        queryset=TransferMaster.objects.filter(is_transferred=False, cancelled=False)
    )
    branch = serializers.IntegerField()
    sub_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    transfer_details = TransferToBranchDetailSerializer(many=True, write_only=True)

    def create(self, validated_data):
        transfer_master = validated_data['transfer_master']
        transfer_master.is_transferred = True
        transfer_master.save()
        save_transfer_data_to_branch(validated_data)

        return validated_data

    def validate(self, attrs):
        if attrs['transfer_master'].transfer_details.all().filter(is_picked=False, cancelled=False).exists():
            raise serializers.ValidationError({"message": "please pick all the orders"})
        return super(TransferToBranchSerializer, self).validate(attrs)


class UpdateTransferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class UpdateTransferSerializer(serializers.ModelSerializer):
    transfer_details = UpdateTransferDetailSerializer(many=True, required=False)

    class Meta:
        model = TransferMaster
        fields = ['sub_total', 'discount_scheme', 'discount_rate', 'total_discountable_amount',
                  'total_taxable_amount', 'total_non_taxable_amount', 'total_discount',
                  'total_tax', 'grand_total', 'remarks', 'transfer_details']

    def update(self, instance, validated_data):
        current_date = timezone.now()
        created_by = current_user.get_created_by(self.context)
        try:
            transfer_details = validated_data.pop('transfer_details')
        except KeyError:
            transfer_details = []
        instance.sub_total = validated_data.get("sub_total", instance.sub_total)
        instance.discount_scheme = validated_data.get("discount_scheme", instance.discount_scheme)
        instance.total_discount = validated_data.get("total_discount", instance.total_discount)
        instance.discount_rate = validated_data.get("discount_rate", instance.discount_rate)
        instance.total_discountable_amount = validated_data.get("total_discountable_amount",
                                                                instance.total_discountable_amount)
        instance.total_taxable_amount = validated_data.get("total_taxable_amount", instance.total_taxable_amount)
        instance.total_non_taxable_amount = validated_data.get("total_non_taxable_amount",
                                                               instance.total_non_taxable_amount)
        instance.total_tax = validated_data.get("total_tax", instance.total_tax)
        instance.grand_total = validated_data.get("grand_total", instance.grand_total)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.save()
        for transfer_detail in transfer_details:
            TransferDetail.objects.create(
                **transfer_detail, created_by=created_by, created_date_ad=current_date,
                transfer_master=instance
            )

        return instance
