from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.custom_lib.functions import current_user
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs, get_fiscal_year_code_ad
from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from src.item_serialization.unique_item_serials import generate_packtype_serial, packing_type_detail_code_list
from ..models import (PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge)
from ..purchase_unique_id_generator import generate_purchase_no, generate_batch_no


class SaveDirectPurchasePaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePaymentDetail
        fields = ['id', 'payment_mode', 'amount', 'payment_id', 'remarks']
        read_only_fields = ['created_date_ad', 'created_date_bs']


class SaveDirectPurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseAdditionalCharge
        fields = ['id', 'charge_type', 'amount', 'remarks']
        read_only_fields = ['created_date_ad', 'created_date_bs']


class SaveDirectPurchasePackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        exclude = ["pack_type_code"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveDirectPurchasePackingTypeCodeSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = SaveDirectPurchasePackingTypeDetailCodeSerializer(many=True, required=False)
    pack_no = serializers.IntegerField(write_only=True)

    class Meta:
        model = PackingTypeCode
        exclude = ["purchase_detail"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'code']
        extra_kwargs = {
            'pack_no': {'write_only': True}
        }


class SaveDirectPurchaseDetailSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = SaveDirectPurchasePackingTypeCodeSerializer(many=True)

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'item', 'purchase_cost', 'sale_cost', 'item_category',
                  'qty', 'pack_qty', 'free_purchase', 'packing_type', 'packing_type_detail',
                  'taxable', 'tax_rate', 'tax_amount', 'discountable', 'expirable', 'discount_rate',
                  'discount_amount', 'gross_amount', 'net_amount', 'expiry_date_ad', 'expiry_date_bs',
                  'batch_no', 'created_date_ad', 'created_date_bs', 'pu_pack_type_codes']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'item_category', 'batch_no']


class SaveDirectPurchaseMasterSerializer(serializers.ModelSerializer):
    purchase_details = SaveDirectPurchaseDetailSerializer(many=True, required=True)
    payment_details = SaveDirectPurchasePaymentDetailSerializer(many=True)
    additional_charges = SaveDirectPurchaseAdditionalChargeSerializer(many=True)

    class Meta:
        model = PurchaseMaster
        exclude = ['app_type', 'device_type', 'fiscal_session_ad', 'fiscal_session_bs']
        read_only_fields = ['created_by', 'created_date_bs', 'created_date_ad',
                            'purchase_no', 'purchase_type']
        extra_kwargs = {
            "department": {"required": True}
        }

    def create(self, validated_data):
        created_by = current_user.get_created_by(self.context)
        validated_data['created_by'] = created_by
        validated_data['purchase_no'] = generate_purchase_no(1)
        validated_data['purchase_type'] = 1
        date_now = timezone.now()
        purchase_details = validated_data.pop('purchase_details')
        payment_details = validated_data.pop('payment_details')
        additional_charges = validated_data.pop('additional_charges')
        current_fiscal_session_short_ad = get_fiscal_year_code_ad()
        current_fiscal_session_short_bs = get_fiscal_year_code_bs()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)
        except Exception as e:
            raise serializers.ValidationError("fiscal session does not match")
        purchase_master = PurchaseMaster.objects.create(**validated_data,
                                                        created_date_ad=date_now,
                                                        fiscal_session_ad=fiscal_session_ad,
                                                        fiscal_session_bs=fiscal_session_bs)
        for payment_detail in payment_details:
            PurchasePaymentDetail.objects.create(
                **payment_detail, purchase_master=purchase_master,
                created_by=created_by,
                created_date_ad=date_now
            )
        for additional_charge in additional_charges:
            PurchaseAdditionalCharge.objects.create(
                **additional_charge, purchase_master=purchase_master,
                created_by=created_by,
                created_date_ad=date_now
            )

        for purchase_detail in purchase_details:
            pack_type_codes = purchase_detail.pop('pu_pack_type_codes')
            if purchase_detail.get('pack_qty', None):
                pack_qty = purchase_detail.pop('pack_qty')
            purchase_detail["batch_no"] = generate_batch_no()
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

            # Validation for ref_purchase_detail  quantity should not be greater than order_qty
            # if "ref_purchase_detail" in purchase_detail:
            #     if purchase_detail['ref_purchase_detail'] is not None:
            #         # print(purchase_detail)
            #         # print(purchase)
            #         reference_qty = purchase_detail['ref_purchase_detail'].qty
            #         # print( purchase_detail['ref_purchase_detail'].qty) # approved qty
            #         # print(purchase_detail['qty']) # order qty
            #         if reference_qty < purchase_detail['qty']: #
            #             raise serializer.ValidationError({ f'item {purchase_detail["item"].name}': f' Approved quantity :{purchase_detail["qty"]} should less than or equal to order quantity:{reference_qty} '})

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
                        f'item {purchase_detail["item"].name}': f'gross_amount calculation not valid, should be {gross_amount}'})
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
                    raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                                                           f'tax_amount calculation not valid : should be {tax_amount}'})
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
                raise serializers.ValidationError(
                    {
                        f'item {purchase_detail["item"].name}': f'net_amount calculation not valid : should be {net_amount}'})
            grand_total = grand_total + net_amount

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                {'total_discountable_amount':
                     f'total_discountable_amount calculation {data["total_discountable_amount"]} not valid: should be {total_discountable_amount}'}
            )

        # validation for discount rate
        # calculated_total_discount_amount = (data['total_discountable_amount'] * data['discount_rate']) / Decimal(
        #     '100.00')
        # calculated_total_discount_amount = calculated_total_discount_amount.quantize(quantize_places)
        # if calculated_total_discount_amount != data['total_discount']:
        #     raise serializer.ValidationError(
        #         'total_discount got {} not valid: expected {}'.format(data['total_discount'],
        #                                                               calculated_total_discount_amount)
        #     )

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

        # validation for total_discount
        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'], total_discount)
            )

        # validation for total_tax
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        # validation for grand_total
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
            )

        return data
