from rest_framework import serializers
from decimal import Decimal
from src.purchase.models import PurchaseMaster, PurchaseDetail, PurchasePaymentDetail
from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from src.purchase.purchase_return_serializer import (
    PurchaseDetailReturnSerializer, PackingTypeCodePurchaseReturnSerializer,
    PackingTypeDetailCodePurchaseReturnSerializer, PaymentDetailReturnSerializer)
from src.custom_lib.functions import current_user
from django.utils import timezone
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.item_serialization.unique_item_serials import (generate_packtype_detail_serial,
                                                        generate_packtype_serial, packing_type_detail_code_list
                                                        )


class StockSubtractionPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    ref_packing_type_detail_code = serializers.PrimaryKeyRelatedField(
        queryset=PackingTypeDetailCode.objects.filter(ref_packing_type_detail_code__isnull=True,
                                                      packingtypedetailcode__isnull=True), required=True)

    class Meta:
        model = PackingTypeDetailCode
        exclude = ['pack_type_code', 'created_date_ad', 'created_date_bs', 'created_by', 'app_type', 'device_type']


class StockSubtractionPackingTypeCodeSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = StockSubtractionPackingTypeDetailCodeSerializer(many=True)
    ref_packing_type_code = serializers.PrimaryKeyRelatedField(
        queryset=PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True), required=True)

    class Meta:
        model = PackingTypeCode
        exclude = ['purchase_detail', 'created_date_ad', 'created_date_bs', 'created_by', 'app_type', 'device_type']


class StockSubtractionPurchaseDetailsSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = StockSubtractionPackingTypeCodeSerializer(many=True)
    ref_purchase_detail = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseDetail.objects.filter(ref_purchase_detail__isnull=True), required=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['purchase', 'device_type', 'app_type', 'expiry_date_ad', 'expiry_date_bs']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'batch_no']


class SaveStockSubtractionSerializer(serializers.ModelSerializer):
    purchase_details = StockSubtractionPurchaseDetailsSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')

    class Meta:
        model = PurchaseMaster
        exclude = ('bill_no', 'bill_date_ad', 'bill_date_bs', 'due_date_ad',
                   'due_date_bs', 'device_type', 'app_type')
        read_only_fields = ['fiscal_session_ad', 'fiscal_session_bs', 'created_by', 'created_date_ad',
                            'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'discount_scheme', 'bill_no', 'due_date_ad', 'ref_purchase', 'ref_purchase_order'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        purchase_details = validated_data.pop('purchase_details')

        # set fiscal year for purchase master
        # get current fiscal year and compare it to FiscalSessionAD and FiscalSessionBS
        current_fiscal_session_short_ad = get_fiscal_year_code_ad()
        current_fiscal_session_short_bs = get_fiscal_year_code_bs()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)
        except:
            raise serializers.ValidationError("fiscal session does not match")

        purchase_master = PurchaseMaster.objects.create(**validated_data, created_date_ad=date_now,
                                                        fiscal_session_ad=fiscal_session_ad,
                                                        fiscal_session_bs=fiscal_session_bs)

        for purchase_detail in purchase_details:
            purchase_detail.pop('pack_qty')
            pu_pack_type_codes = purchase_detail.pop('pu_pack_type_codes')
            purchase_detail_db = PurchaseDetail.objects.create(**purchase_detail, purchase=purchase_master,
                                                               pack_qty=purchase_detail[
                                                                   'packing_type_detail'].pack_qty,
                                                               created_by=validated_data['created_by'],
                                                               created_date_ad=date_now)

            for pu_pack_type_code in pu_pack_type_codes:
                pack_type_detail_codes = pu_pack_type_code.pop('pack_type_detail_codes')
                code = generate_packtype_serial()
                pack_type_code_db = PackingTypeCode.objects.create(
                    code=code,
                    created_by=validated_data['created_by'], created_date_ad=date_now,
                    purchase_detail=purchase_detail_db,
                    ref_packing_type_code=pu_pack_type_code['ref_packing_type_code']
                )

                for pack_type_detail in pack_type_detail_codes:
                    PackingTypeDetailCode.objects.create(
                        code=pack_type_detail['code'],
                        created_by=validated_data['created_by'],
                        created_date_ad=date_now,
                        pack_type_code=pack_type_code_db,
                        ref_packing_type_detail_code=pack_type_detail['ref_packing_type_detail_code']
                    )

        return purchase_master

    def validate(self, data):
        quantize_places = Decimal(10) ** -2
        # initialize variables to check
        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        purchase_details = data['purchase_details']
        for purchase in purchase_details:
            purchase_detail = {}
            key_values = zip(purchase.keys(), purchase.values())
            for key, values in key_values:
                purchase_detail[key] = values
            # validation for amount values less than or equal to 0 "Zero"
            if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0 or \
                    purchase_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                            ' cannot be less than 0'})

            if purchase_detail['purchase_cost'] <= 0 or purchase_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost and quantity cannot be less than'
                                                            ' or equals to 0'})
            if purchase_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {purchase_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = purchase_detail['purchase_cost'] * purchase_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != purchase_detail['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {purchase_detail["item"].name}': f'gross_amount calculation not valid : should be {gross_amount}'})
            sub_total = sub_total + gross_amount

            # validation for discount amount
            if purchase_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + purchase_detail['gross_amount']
                discount_rate = (purchase_detail['discount_amount'] *
                                 Decimal('100')) / (purchase_detail['purchase_cost'] *
                                                    purchase_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != purchase_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {purchase_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + purchase_detail['discount_amount']
            elif purchase_detail['discountable'] is False and purchase_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                                                       f'discount_amount {purchase_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - purchase_detail['discount_amount']
            if purchase_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = purchase_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != purchase_detail['tax_amount']:
                    raise serializers.ValidationError(
                        {
                            f'item {purchase_detail["item"].name}': f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif purchase_detail['taxable'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((
                purchase_detail['discount_amount']))) + \
                         ((gross_amount - (
                             purchase_detail['discount_amount'])) *
                          purchase_detail['tax_rate'] / Decimal('100'))

            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_detail['net_amount']:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                    'net_amount calculation not valid : should be {}'.format(
                        net_amount)})
            grand_total = grand_total + net_amount

        # validation for purchase in CREDIT with no supplier
        if data['pay_type'] == 2 and data['supplier'] == '':
            raise serializers.ValidationError('Cannot perform purchase in CREDIT with no supplier')

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                'total_discountable_amount calculation {} not valid: should be {}'.format(
                    data['total_discountable_amount'], total_discountable_amount)
            )

        # validation for total_taxable_amount
        if total_taxable_amount != data['total_taxable_amount']:
            raise serializers.ValidationError(
                'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
                                                                                     total_taxable_amount)
            )

        # validation for total_nontaxable_amount
        if total_nontaxable_amount != data['total_non_taxable_amount']:
            raise serializers.ValidationError(
                'total_non_taxable_amount calculation {} not valid: should be {}'.format(
                    data['total_non_taxable_amount'],
                    total_nontaxable_amount)
            )

        # check subtotal , total discount , total tax and grand total
        if sub_total != data['sub_total']:
            raise serializers.ValidationError(
                'sub_total calculation not valid: should be {}'.format(sub_total)
            )

        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'],
                                                                               total_discount)
            )
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
            )

        return data
