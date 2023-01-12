from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.custom_lib.functions.current_user import get_created_by
from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from .models import PurchaseDetail, PurchaseMaster, PurchasePaymentDetail
from .purchase_unique_id_generator import generate_purchase_no


class PackingTypeDetailCodePurchaseReturnSerializer(serializers.ModelSerializer):
    ref_packing_type_detail_code = serializers.PrimaryKeyRelatedField(
        queryset=PackingTypeDetailCode.objects.filter(ref_packing_type_detail_code__isnull=True), required=True)

    class Meta:
        model = PackingTypeDetailCode
        exclude = ['pack_type_code', 'created_date_ad', 'created_date_bs', 'created_by', 'app_type', 'device_type']


class PackingTypeCodePurchaseReturnSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = PackingTypeDetailCodePurchaseReturnSerializer(many=True)
    ref_packing_type_code = serializers.PrimaryKeyRelatedField(
        queryset=PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True), required=True)

    class Meta:
        model = PackingTypeCode
        exclude = ['purchase_detail', 'created_date_ad', 'created_date_bs', 'created_by', 'app_type', 'device_type']


class PaymentDetailReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePaymentDetail
        exclude = ['purchase_master', 'device_type', 'app_type']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class PurchaseDetailReturnSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = PackingTypeCodePurchaseReturnSerializer(many=True)
    ref_purchase_detail = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseDetail.objects.filter(ref_purchase_detail__isnull=True), required=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['purchase', 'device_type', 'app_type']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'batch_no']


class PurchaseReturnSerializer(serializers.ModelSerializer):
    purchase_details = PurchaseDetailReturnSerializer(many=True)
    payment_details = PaymentDetailReturnSerializer(many=True)
    ref_purchase = serializers.PrimaryKeyRelatedField(queryset=PurchaseMaster.objects.filter(ref_purchase__isnull=True),
                                                      required=True)

    class Meta:
        model = PurchaseMaster
        fields = [
            'purchase_details', 'payment_details', 'ref_purchase',
            'pay_type', 'sub_total', 'total_discount', 'discount_rate',
            'discount_scheme', 'total_discountable_amount', 'total_taxable_amount',
            'total_non_taxable_amount', 'total_tax', 'grand_total', 'round_off_amount',
            'supplier', 'bill_no', 'bill_date_ad', 'bill_date_bs',
            'chalan_no', 'due_date_ad', 'remarks', 'ref_purchase_order',
            'created_by', 'created_date_ad', 'created_date_bs', 'department'
        ]
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        created_by = get_created_by(self.context)
        date_now = timezone.now()
        purchase_no = generate_purchase_no(2)
        fiscal_session_ad = FiscalSessionAD.objects.first()
        fiscal_session_bs = FiscalSessionBS.objects.first()
        purchase_details = validated_data.pop('purchase_details')
        payment_details = validated_data.pop('payment_details')
        purchase_master = PurchaseMaster.objects.create(
            created_by=created_by, created_date_ad=date_now, purchase_no=purchase_no,
            purchase_type=2, **validated_data, fiscal_session_ad=fiscal_session_ad,
            fiscal_session_bs=fiscal_session_bs
        )

        for purchase_detail in purchase_details:
            pu_pack_type_codes = purchase_detail.pop('pu_pack_type_codes')
            purchase_detail_db = PurchaseDetail.objects.create(
                **purchase_detail, created_by=created_by, created_date_ad=date_now,
                purchase=purchase_master
            )
            for pu_pack_type_code in pu_pack_type_codes:
                pack_type_detail_codes = pu_pack_type_code.pop('pack_type_detail_codes')
                pack_type_code_db = PackingTypeCode.objects.create(
                    created_by=created_by, created_date_ad=date_now, **pu_pack_type_code,
                    purchase_detail=purchase_detail_db
                )
                for pack_type_detail in pack_type_detail_codes:
                    PackingTypeDetailCode.objects.create(
                        created_by=created_by, created_date_ad=date_now, **pack_type_detail,
                        pack_type_code=pack_type_code_db
                    )

        for payment_detail in payment_details:
            PurchasePaymentDetail.objects.create(
                **payment_detail, created_by=created_by, created_date_ad=date_now,
                purchase_master=purchase_master
            )

        return purchase_master
