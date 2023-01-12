from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import (FiscalSessionAD, FiscalSessionBS)
# custom functions
from src.custom_lib.functions.current_user import get_created_by
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from src.customer_order.models import OrderMaster
from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
# imported models
from .models import SaleAdditionalCharge, SaleDetail, SaleMaster, SalePaymentDetail


# For Read and Write View
class SaveSalePaymentDetailReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePaymentDetail
        exclude = ['sale_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# for Write
class SaveSaleAdditionalChargeReturn(serializers.ModelSerializer):
    class Meta:
        model = SaleAdditionalCharge
        exclude = ['sale_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class SalePackingTypeDetailCodeReturnSerializer(serializers.ModelSerializer):
    ref_sale_packing_type_detail_code = serializers.PrimaryKeyRelatedField(
        queryset=SalePackingTypeDetailCode.objects.filter(ref_sale_packing_type_detail_code__isnull=True), required=True
    )

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'ref_sale_packing_type_detail_code']


class SalePackingTypeCodeSaleReturnSerializer(serializers.ModelSerializer):
    ref_sale_packing_type_code = serializers.PrimaryKeyRelatedField(
        queryset=SalePackingTypeCode.objects.filter(ref_sale_packing_type_code__isnull=True), required=True
    )
    sale_packing_type_detail_code = SalePackingTypeDetailCodeReturnSerializer(many=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'packing_type_code', 'customer_order_detail', 'ref_sale_packing_type_code',
                  'sale_packing_type_detail_code']


class SaveSaleDetailReturnSerializer(serializers.ModelSerializer):
    sale_packing_type_code = SalePackingTypeCodeSaleReturnSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale_master.sale_no')
    ref_sale_detail = serializers.PrimaryKeyRelatedField(
        queryset=SaleDetail.objects.filter(ref_sale_detail__isnull=True)
    )
    pack_qty = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), required=False)

    class Meta:
        model = SaleDetail
        exclude = ['sale_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# For Read and Write View
class SaveSaleMasterReturnSerializer(serializers.ModelSerializer):
    sale_details = SaveSaleDetailReturnSerializer(many=True)
    payment_details = SaveSalePaymentDetailReturnSerializer(many=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name')
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name')
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    sale_additional_charges = SaveSaleAdditionalChargeReturn(many=True)
    ref_sale_master = serializers.PrimaryKeyRelatedField(
        queryset=SaleMaster.objects.filter(sale_type=1)
    )
    ref_order_master = serializers.PrimaryKeyRelatedField(
        queryset=OrderMaster.objects.filter(status=2)
    )

    class Meta:
        model = SaleMaster
        fields = "__all__"
        read_only_fields = ['fiscal_session_ad', 'fiscal_session_bs',
                            'created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        quantize_places = Decimal(10) ** -2

        validated_data['created_by'] = get_created_by(self.context)
        date_now = timezone.now()
        sale_details = validated_data.pop('sale_details')
        if not sale_details:
            serializers.ValidationError("Please provide at least one sale detail")

        payment_details = validated_data.pop('payment_details')
        # print(payment_details)
        additional_charges = validated_data.pop('sale_additional_charges')
        if not payment_details:
            serializers.ValidationError("Please provide payment details")

        current_fiscal_session_short_ad = get_fiscal_year_code_ad()
        current_fiscal_session_short_bs = get_fiscal_year_code_bs()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)
        except:
            raise serializers.ValidationError("fiscal session does not match")

        # save sale data
        validated_data['return_dropped'] = False
        sale_master = SaleMaster.objects.create(**validated_data, created_date_ad=date_now,
                                                fiscal_session_ad=fiscal_session_ad,
                                                fiscal_session_bs=fiscal_session_bs)

        for sale_detail in sale_details:
            sale_packing_type_codes = sale_detail.pop('sale_packing_type_code')
            sale_detail_db = SaleDetail.objects.create(**sale_detail, sale_master=sale_master,
                                                       created_by=validated_data['created_by'],
                                                       created_date_ad=date_now)
            for sale_packing_type_code in sale_packing_type_codes:
                sale_packing_type_detail_codes = sale_packing_type_code.pop('sale_packing_type_detail_code')
                sale_packing_type_code_db = SalePackingTypeCode.objects.create(
                    **sale_packing_type_code, sale_detail=sale_detail_db
                )

                for sale_packing_type_detail_code in sale_packing_type_detail_codes:
                    SalePackingTypeDetailCode.objects.create(
                        **sale_packing_type_detail_code, sale_packing_type_code=sale_packing_type_code_db
                    )

            # save sale packing type codes

        for additional_charge in additional_charges:
            SaleAdditionalCharge.objects.create(**additional_charge, sale_master=sale_master,
                                                created_by=validated_data['created_by'],
                                                created_date_ad=date_now)

        """________________________calculation for  payment ______________________________________"""
        # Payment detail for CASH payment
        if validated_data['pay_type'] == 1:
            # all payment details are stored in PaymentDetails Model
            for payment_detail in payment_details:
                SalePaymentDetail.objects.create(
                    **payment_detail, sale_master=sale_master,
                    created_by=validated_data['created_by'], created_date_ad=date_now
                )
        return sale_master


class SaleReturnDropSerializer(serializers.Serializer):
    sale_master = serializers.PrimaryKeyRelatedField(
        queryset=SaleMaster.objects.filter(return_dropped=False, sale_type=2)
    )
    sale_serial_nos = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=SalePackingTypeDetailCode.objects.filter(
            sale_packing_type_code__sale_detail__sale_master__return_dropped=False

        ).annotate(sale_master=F('sale_packing_type_code__sale_detail__sale_master_id')).distinct()
    ))

    def create(self, validated_data):
        sale_master = validated_data['sale_master']
        sale_serial_nos = validated_data['sale_serial_nos']
        sale_details = SaleDetail.objects.filter(sale_master=sale_master).aggregate(total_qty=Sum('qty'))
        if len(sale_serial_nos) != sale_details['total_qty']:
            raise serializers.ValidationError({"error": "please scan all/only serial nos for this sale return"})
        for sale_serial_no in sale_serial_nos:
            print(sale_serial_no.sale_master)
            if sale_serial_no.sale_master != sale_master.id:
                raise serializers.ValidationError(
                    {"error": f"serial no {sale_serial_no.sale_master} does not match with this sale return"})

        sale_master.return_dropped = True
        sale_master.save()
        return validated_data


class SaleReturnInfoPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source="packing_type_detail_code.code", allow_null=True)

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'ref_sale_packing_type_detail_code', "code"]
        read_only_fields = fields


class SaleReturnInfoPackingTypeCodeSaleSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = SaleReturnInfoPackingTypeDetailCodeSerializer(many=True)
    code = serializers.ReadOnlyField(source="packing_type_code.code", allow_null=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', "code", 'packing_type_code', 'customer_order_detail', 'ref_sale_packing_type_code',
                  'sale_packing_type_detail_code']
        read_only_fields = fields


class SaleDetailReturnInfoSerializer(serializers.ModelSerializer):
    sale_packing_type_code = SaleReturnInfoPackingTypeCodeSaleSerializer(many=True, read_only=True)
    item_name = serializers.ReadOnlyField(source='item.name')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')
    code_name = serializers.ReadOnlyField(source='item.code')
    unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    expiry_date_ad = serializers.ReadOnlyField(source='ref_purchase_detail.expiry_date_ad')
    expiry_date_bs = serializers.ReadOnlyField(source='ref_purchase_detail.expiry_date_bs')
    location = serializers.ReadOnlyField(source='item.location')
    batch_no = serializers.ReadOnlyField(source='ref_purchase_detail.batch_no')

    class Meta:
        model = SaleDetail
        exclude = ['created_date_ad', 'created_date_bs', 'ref_sale_detail', 'created_by']
