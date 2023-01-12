import decimal

from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.custom_lib.functions import current_user
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from src.item_serialization.models import PackingTypeCode
from src.purchase.purchase_unique_id_generator import generate_batch_no
# Models from purchase app
from .models import (PurchaseAdditionalCharge, PurchaseDetail, PurchaseDocument, PurchaseMaster,
                     PurchaseOrderDetail, PurchaseOrderMaster, PurchasePaymentDetail)
from .purchase_unique_id_generator import generate_purchase_no

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


class PaymentDetailVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePaymentDetail
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class PurchaseAdditionalChargeVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseAdditionalCharge
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class PurchaseDocumentsVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDocument
        exclude = ['purchase_main']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class PurchaseDetailVerifySerializer(serializers.ModelSerializer):
    ref_purchase_order_detail = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrderDetail.objects.filter(purchase_order__order_type=3), required=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['purchase', 'ref_purchase_detail']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'batch_no']

    def to_representation(self, instance):
        my_fields = {'expiry_date_ad', 'ref_purchase_order_detail', 'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# nested purchase_order_serializer for purchase master with purchase detail, payment detail and
# additional charges for write_only views
class PurchaseMasterVerifySerializer(serializers.ModelSerializer):
    purchase_details = PurchaseDetailVerifySerializer(many=True)
    payment_details = PaymentDetailVerifySerializer(many=True)
    additional_charges = PurchaseAdditionalChargeVerifySerializer(many=True)
    purchase_documents = PurchaseDocumentsVerifySerializer(many=True)
    ref_purchase_order = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrderMaster.objects.filter(order_type=3),
                                                            required=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'fiscal_session_ad',
                            'fiscal_session_bs', 'purchase_no']

        extra_kwargs = {
            "department": {'required': True}
        }

    def to_representation(self, instance):
        my_fields = {'discount_scheme', 'bill_no', 'due_date_ad', 'ref_purchase', 'ref_purchase_order',
                     'additional_charges'}
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
        validated_data['purchase_no'] = generate_purchase_no(1)
        date_now = timezone.now()
        purchase_details = validated_data.pop('purchase_details')
        payment_details = validated_data.pop('payment_details')
        additional_charges = validated_data.pop('additional_charges')
        purchase_documents = validated_data.pop('purchase_documents')

        current_fiscal_session_short_ad = get_fiscal_year_code_ad()
        current_fiscal_session_short_bs = get_fiscal_year_code_bs()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.first()
            fiscal_session_bs = FiscalSessionBS.objects.first()

        except:
            raise serializers.ValidationError("fiscal session does not match")

        purchase_master = PurchaseMaster.objects.create(**validated_data, created_date_ad=date_now,
                                                        fiscal_session_ad=fiscal_session_ad,
                                                        fiscal_session_bs=fiscal_session_bs)

        for purchase_detail in purchase_details:
            purchase_detail["batch_no"] = generate_batch_no()
            purchase_detail_db = PurchaseDetail.objects.create(**purchase_detail, purchase=purchase_master,
                                                               created_by=validated_data['created_by'],
                                                               created_date_ad=date_now)
            # update item serialization for purchase
            pack_type_codes = PackingTypeCode.objects.filter(
                purchase_order_detail=purchase_detail['ref_purchase_order_detail'].id
            )
            for packing_type_code in pack_type_codes:
                packing_type_code.purchase_detail = purchase_detail_db
                packing_type_code.save()
        for payment_detail in payment_details:
            PurchasePaymentDetail.objects.create(**payment_detail, purchase_master=purchase_master,
                                                 created_by=validated_data['created_by'], created_date_ad=date_now)

        for additional_charge in additional_charges:
            PurchaseAdditionalCharge.objects.create(**additional_charge, purchase_master=purchase_master,
                                                    created_by=validated_data['created_by'], created_date_ad=date_now)

        for purchase_document in purchase_documents:
            PurchaseDocument.objects.create(**purchase_document, purchase_main=purchase_master,
                                            created_by=validated_data['created_by'], created_date_ad=date_now)
        return purchase_master

    # def validate(self, data):
    #     quantize_places = Decimal(10) ** -2
    #     # initialize variables to check
    #     sub_total = Decimal('0.00')
    #     total_discount = Decimal('0.00')
    #     total_discountable_amount = Decimal('0.00')
    #     total_taxable_amount = Decimal('0.00')
    #     total_nontaxable_amount = Decimal('0.00')
    #     total_tax = Decimal('0.00')
    #     net_amount = Decimal('0.00')
    #     grand_total = Decimal('0.00')
    #     purchase_details = data['purchase_details']

    #     for purchase in purchase_details:
    #         # purchase_order_detail = {}
    #         purchase_detail = {}
    #         key_values = zip(purchase.keys(), purchase.values())
    #         # key_values_order = zip(purchase_order.keys(), purchase_order.values())
    #         for key, values in key_values:
    #             purchase_detail[key] = values

    #         # if "ref_purchase" in purchase_master:
    #         #     if purchase_master['ref_purchase'] is not None:
    #         #         ref_pay_type = purchase_master['ref_purchase'].pay_type

    #         # validation for amount values less than or equal to 0 "Zero"
    #         if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0 or \
    #                 purchase_detail['sale_cost'] < 0:
    #             raise serializer.ValidationError({
    #                 f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
    #                                                         ' cannot be less than 0'})

    #         if purchase_detail['purchase_cost'] <= 0 or purchase_detail['qty'] <= 0:
    #             raise serializer.ValidationError({
    #                 f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost and quantity cannot be less than'
    #                                                         ' or equals to 0'})
    #         if purchase_detail['discount_rate'] > 100:
    #             raise serializer.ValidationError(
    #                 {f'item {purchase_detail["item"].name}': 'Discount rate can not be greater than 100.'})

    #         # validation for gross_amount
    #         gross_amount = purchase_detail['purchase_cost'] * purchase_detail['qty']
    #         gross_amount = gross_amount.quantize(quantize_places)
    #         if gross_amount != purchase_detail['gross_amount']:
    #             raise serializer.ValidationError(
    #                 {
    #                     f'item {purchase_detail["item"].name}': f'gross_amount calculation not valid : should be {gross_amount}'})
    #         if purchase_detail['free_purchase'] is False:
    #             sub_total = sub_total + gross_amount

    #             # validation for discount amount
    #         if purchase_detail['discountable'] is True and purchase_detail['free_purchase'] is False:
    #             total_discountable_amount = total_discountable_amount + purchase_detail['gross_amount']
    #             discount_rate = (purchase_detail['discount_amount'] *
    #                              Decimal('100')) / (purchase_detail['purchase_cost'] *
    #                                                 purchase_detail['qty'])
    #             discount_rate = discount_rate.quantize(quantize_places)
    #             # if discount_rate != purchase_detail['discount_rate']:
    #             #     raise serializer.ValidationError(
    #             #         {
    #             #             f'item {purchase_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
    #             total_discount = total_discount + purchase_detail['discount_amount']
    #         elif purchase_detail['discountable'] is False and purchase_detail['discount_amount'] > 0:
    #             raise serializer.ValidationError({f'item {purchase_detail["item"].name}':
    #                                                    f'discount_amount {purchase_detail["discount_amount"]} can not be '
    #                                                    f'given to item with discountable = False'})

    #         # validation for tax amount
    #         probable_taxable_amount = gross_amount - purchase_detail['discount_amount']
    #         if purchase_detail['taxable'] is True and purchase_detail['free_purchase'] is False:
    #             total_taxable_amount = total_taxable_amount + probable_taxable_amount
    #             tax_amount = purchase_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
    #             tax_amount = tax_amount.quantize(quantize_places)
    #             if tax_amount != purchase_detail['tax_amount']:
    #                 raise serializer.ValidationError(
    #                     {f'item {purchase_detail["item"].name}':f'tax_amount calculation not valid : should be {tax_amount}'})
    #             total_tax = total_tax + tax_amount
    #         elif purchase_detail['taxable'] is False and purchase_detail['free_purchase'] is False:
    #             total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

    #         # validation for net_amount
    #         net_amount = (gross_amount - ((
    #                                        purchase_detail['discount_amount']) )) + \
    #                      ((gross_amount - (
    #                                        purchase_detail['discount_amount'])) *
    #                       purchase_detail['tax_rate'] / Decimal('100'))

    #         net_amount = net_amount.quantize(quantize_places)
    #         if net_amount != purchase_detail['net_amount']:
    #             raise serializer.ValidationError({f'item {purchase_detail["item"].name}':
    #                 'net_amount calculation not valid : should be {}'.format(net_amount)})
    #         if purchase_detail['free_purchase'] is False:
    #             grand_total = grand_total + net_amount

    #     # validation for purchase in CREDIT with no supplier
    #     if data['pay_type'] == 2 and data['supplier'] == '':
    #         raise serializer.ValidationError('Cannot perform purchase in CREDIT with no supplier')

    #     # calculating additional charge
    #     try:
    #         data['additional_charges']
    #     except KeyError:
    #         raise serializer.ValidationError(
    #             {'additional_charges': 'Provide additional_charge key'}
    #         )
    #     additional_charges = data['additional_charges']
    #     add_charge = Decimal('0.00')
    #     for additional_charge in additional_charges:
    #         add_charge = add_charge + additional_charge['amount']

    #     # validation for total_discountable_amount
    #     if total_discountable_amount != data['total_discountable_amount']:
    #         raise serializer.ValidationError(
    #             'total_discountable_amount calculation {} not valid: should be {}'.format(
    #                 data['total_discountable_amount'], total_discountable_amount)
    #         )

    #     # validation for discount rate
    #     # calculated_total_discount_amount = (data['total_discountable_amount'] * data['discount_rate']) / Decimal(
    #     #     '100.00')
    #     # calculated_total_discount_amount = calculated_total_discount_amount.quantize(quantize_places)
    #     # if calculated_total_discount_amount != data['total_discount']:
    #     #     raise serializer.ValidationError(
    #     #         'total_discount got {} not valid: expected {}'.format(data['total_discount'],
    #     #                                                               calculated_total_discount_amount)
    #     #     )

    #     # validation for total_taxable_amount
    #     if total_taxable_amount != data['total_taxable_amount']:
    #         raise serializer.ValidationError(
    #             'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
    #                                                                                  total_taxable_amount)
    #         )

    #     # validation for total_nontaxable_amount
    #     if total_nontaxable_amount != data['total_non_taxable_amount']:
    #         raise serializer.ValidationError(
    #             'total_non_taxable_amount calculation {} not valid: should be {}'.format(
    #                 data['total_non_taxable_amount'],
    #                 total_nontaxable_amount)
    #         )

    #     # check subtotal , total discount , total tax and grand total
    #     if sub_total != data['sub_total']:
    #         raise serializer.ValidationError(
    #             'sub_total calculation not valid: should be {}'.format(sub_total)
    #         )

    #     if total_discount != data['total_discount']:
    #         raise serializer.ValidationError(
    #             'total_discount calculation {} not valid: should be {}'.format(data['total_discount'],
    #                                                                            total_discount)
    #         )
    #     if total_tax != data['total_tax']:
    #         raise serializer.ValidationError(
    #             'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
    #         )

    #     grand_total = grand_total + add_charge

    #         #check where is there  oranizaiantion rule or not
    #     try:
    #             organization_rule = OrganizationRule.objects.first()
    #     except:
    #         raise ValueError("Object not found, Create Organization Rule")

    #     if organization_rule.round_off_purchase is True:
    #         grand_total = grand_total.quantize(Decimal("0")); 
    #         if grand_total != data['grand_total']:
    #             raise serializer.ValidationError(
    #                 'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
    #             )

    #     # validation of payment details
    #     try:
    #         data['payment_details']
    #     except KeyError:
    #         raise serializer.ValidationError(
    #             {'payment_details': 'Provide payment details'}
    #         )
    #     try:
    #         data['pay_type']
    #     except KeyError:
    #         raise serializer.ValidationError(
    #             {'pay_type': 'please provide pay_type key'}
    #         )
    #     payment_details = data['payment_details']
    #     total_payment = Decimal('0.00')

    #     for payment_detail in payment_details:
    #         total_payment = total_payment + payment_detail['amount']
    #     if data['pay_type'] == 1:
    #         if total_payment != data['grand_total']:
    #             raise serializer.ValidationError(
    #                 {'amount': 'sum of amount {} should be equal to grand_total {} in pay_type CASH'.format(
    #                     total_payment, data['grand_total'])}
    #             )
    #     elif data['pay_type'] == 2 or data['pay_type'] == 3:
    #         if total_payment > data['grand_total']:
    #             raise serializer.ValidationError(
    #                 {
    #                     'amount': 'Cannot process purchase CREDIT with total paid amount greater than {}'.format(
    #                         data['grand_total'])}
    #             )
    #     return data
