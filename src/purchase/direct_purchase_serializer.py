import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.core_app.models import OrganizationRule
from src.custom_lib.functions import current_user
from src.custom_lib.functions import fiscal_year
from .models import PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, \
    PurchaseAdditionalCharge, PurchaseDocument
from .purchase_unique_id_generator import generate_purchase_no, generate_batch_no


class DirectPurchaseDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDetail
        fields = ['id', 'item', 'item_category', 'purchase_cost', 'sale_cost',
                  'qty', 'pack_qty', 'packing_type', 'packing_type_detail',
                  'taxable', 'tax_rate', 'tax_amount', 'discountable', 'expirable',
                  'discount_rate', 'discount_amount', 'discount_amount', 'gross_amount',
                  'gross_amount', 'net_amount', 'expiry_date_ad', 'expiry_date_bs',
                  'batch_no']
        read_only_fields = ['batch_no']


class DirectPurchasePaymentDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePaymentDetail
        fields = ['id', 'payment_mode', 'amount', 'remarks']


class DirectPurchaseAdditionalChargesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseAdditionalCharge
        fields = ['id', 'charge_type', 'amount', 'remarks']


class DirectPurchaseDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDocument
        fields = ['id', 'title', 'purchase_document_type', 'document_url', 'remarks']


class DirectPurchaseMasterCreateSerializer(serializers.ModelSerializer):
    purchase_details = DirectPurchaseDetailCreateSerializer(many=True)
    payment_details = DirectPurchasePaymentDetailCreateSerializer(many=True)
    additional_charges = DirectPurchaseAdditionalChargesCreateSerializer(many=True)
    purchase_documents = DirectPurchaseDocumentCreateSerializer(many=True)
    chalan_no = serializers.CharField(allow_blank=True, max_length=20)
    bill_no = serializers.CharField(allow_blank=True, max_length=20)

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'purchase_type', 'pay_type',
                  'sub_total', 'total_discount', 'discount_rate', 'discount_scheme',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'total_tax', 'grand_total', 'supplier', 'bill_no',
                  'bill_date_ad', 'bill_date_bs', 'chalan_no', 'remarks',
                  'purchase_details', 'payment_details', 'additional_charges',
                  'purchase_documents']
        read_only_fields = ['purchase_no', 'purchase_type', 'bill_date_bs']
        extra_kwargs = {'supplier': {'required': True}}

    def create(self, validated_data):
        created_date_ad = timezone.now()
        created_by = current_user.get_created_by(self.context)
        purchase_no = generate_purchase_no(purchase_type=1)
        purchase_details = validated_data.pop('purchase_details')
        payment_details = validated_data.pop('payment_details')
        additional_charges = validated_data.pop('additional_charges')
        purchase_documents = validated_data.pop('purchase_documents')
        purchase_type = 1  # 1 => Purchase

        # fiscal sessions
        fiscal_year_ad_short = fiscal_year.get_fiscal_year_code_bs()
        fiscal_year_bs_short = fiscal_year.get_fiscal_year_code_ad()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=fiscal_year_ad_short)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=fiscal_year_bs_short)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {
                    "fiscal_year": "please set fiscal session ad and fiscal session bs in core app"
                }
            )
        purchase_master = PurchaseMaster.objects.create(
            **validated_data, purchase_type=purchase_type, purchase_no=purchase_no,
            created_by=created_by, created_date_ad=created_date_ad,
            fiscal_session_ad=fiscal_session_ad, fiscal_session_bs=fiscal_session_bs
        )
        if not purchase_details:
            raise serializers.ValidationError({'purchase_details': 'please provide purchase details'})
        for purchase_detail in purchase_details:
            batch_no = generate_batch_no()
            PurchaseDetail.objects.create(
                **purchase_detail, batch_no=batch_no,
                created_date_ad=created_date_ad,
                created_by=created_by
            )
        for payment_detail in payment_details:
            PurchasePaymentDetail.objects.create(
                **payment_detail, created_by=created_by,
                created_date_ad=created_date_ad
            )
        for additional_charge in additional_charges:
            PurchaseAdditionalCharge.objects.create(
                **additional_charge, created_by=created_by,
                created_date_ad=created_date_ad
            )
        for purchase_document in purchase_documents:
            PurchaseDocument.objects.create(
                **purchase_document, created_by=created_by,
                created_date_ad=created_date_ad
            )
        return purchase_master

    def validate(self, data):
        quantize_places = decimal.Decimal(10) ** -2
        # initialize variables to check
        sub_total = decimal.Decimal('0.00')
        total_discount = decimal.Decimal('0.00')
        total_discountable_amount = decimal.Decimal('0.00')
        total_taxable_amount = decimal.Decimal('0.00')
        total_nontaxable_amount = decimal.Decimal('0.00')
        total_tax = decimal.Decimal('0.00')
        net_amount = decimal.Decimal('0.00')
        grand_total = decimal.Decimal('0.00')
        purchase_details = data['purchase_details']

        for purchase in purchase_details:
            decimal.getcontext().rounding = decimal.ROUND_HALF_UP
            # purchase_order_detail = {}
            purchase_detail = {}
            key_values = zip(purchase.keys(), purchase.values())
            # key_values_order = zip(purchase_order.keys(), purchase_order.values())
            for key, values in key_values:
                purchase_detail[key] = values

            # validation for amount values less than or equal to 0 "Zero"
            if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate'
                                                            ' cannot be less than 0'})

            if purchase_detail['purchase_cost'] <= 0 or purchase_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost and quantity cannot be '
                                                            'less than or equals to 0'})
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

            # validation for discount amount
            if purchase_detail['discountable'] is True and purchase_detail['free_purchase'] is False:
                total_discountable_amount = total_discountable_amount + purchase_detail['gross_amount']
                discount_rate = (purchase_detail['discount_amount'] *
                                 decimal.Decimal('100')) / (purchase_detail['purchase_cost'] *
                                                            purchase_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                # if discount_rate != purchase_detail['discount_rate']:
                #     raise serializer.ValidationError(
                #         {
                #             f'item {purchase_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + purchase_detail['discount_amount']
            elif purchase_detail['discountable'] is False and purchase_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                                                       f'discount_amount {purchase_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - purchase_detail['discount_amount']
            if purchase_detail['taxable'] is True and purchase_detail['free_purchase'] is False:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = purchase_detail['tax_rate'] * probable_taxable_amount / decimal.Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != purchase_detail['tax_amount']:
                    raise serializers.ValidationError(
                        {
                            f'item {purchase_detail["item"].name}': f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif purchase_detail['taxable'] is False and purchase_detail['free_purchase'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((
                purchase_detail['discount_amount']))) + \
                         ((gross_amount - (
                             purchase_detail['discount_amount'])) *
                          purchase_detail['tax_rate'] / decimal.Decimal('100'))

            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_detail['net_amount']:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                    'net_amount calculation not valid : should be {}'.format(
                        net_amount)})
            if purchase_detail['free_purchase'] is False:
                grand_total = grand_total + net_amount

        # validation for purchase in CREDIT with no supplier
        if data['pay_type'] == 2 and data['supplier'] == '':
            raise serializers.ValidationError('Cannot perform purchase in CREDIT with no supplier')

        # calculating additional charge
        try:
            data['additional_charges']
        except KeyError:
            raise serializers.ValidationError(
                {'additional_charges': 'Provide additional_charge key'}
            )
        additional_charges = data['additional_charges']
        add_charge = decimal.Decimal('0.00')
        for additional_charge in additional_charges:
            add_charge = add_charge + additional_charge['amount']

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                'total_discountable_amount calculation {} not valid: should be {}'.format(
                    data['total_discountable_amount'], total_discountable_amount)
            )

        # validation for discount rate
        # calculated_total_discount_amount = (data['total_discountable_amount'] * data['discount_rate']) / decimal.Decimal(
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

        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'],
                                                                               total_discount)
            )
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        grand_total = grand_total + add_charge

        # check where is there  organization rule or not
        try:
            organization_rule = OrganizationRule.objects.first()
        except ObjectDoesNotExist:
            raise ValueError("Object not found, Create Organization Rule")

        if organization_rule.round_off_purchase is True:
            grand_total = grand_total.quantize(decimal.Decimal("0"))
            if grand_total != data['grand_total']:
                raise serializers.ValidationError(
                    'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
                )

        # validation of payment details
        try:
            data['payment_details']
        except KeyError:
            raise serializers.ValidationError(
                {'payment_details': 'Provide payment details'}
            )
        try:
            data['pay_type']
        except KeyError:
            raise serializers.ValidationError(
                {'pay_type': 'please provide pay_type key'}
            )
        payment_details = data['payment_details']
        total_payment = decimal.Decimal('0.00')

        for payment_detail in payment_details:
            total_payment = total_payment + payment_detail['amount']
        if data['pay_type'] == 1:
            if total_payment != data['grand_total']:
                raise serializers.ValidationError(
                    {'amount': 'sum of amount {} should be equal to grand_total {} in pay_type CASH'.format(
                        total_payment, data['grand_total'])}
                )
        elif data['pay_type'] == 2:
            if total_payment > data['grand_total']:
                raise serializers.ValidationError(
                    {
                        'amount': 'Cannot process purchase CREDIT with total paid amount greater than {}'.format(
                            data['grand_total'])}
                )
        return data

    def validate_chalan_no(self, chalan_no):
        if self.bill_no == "" and chalan_no == "":
            raise serializers.ValidationError(
                {"chalan_no/bill_no": "Either one should be preset"}
            )
        return chalan_no
