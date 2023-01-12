import decimal
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import DiscountScheme
from src.custom_lib.functions import current_user
from src.customer.models import Customer
from src.item.models import Item
from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from .chalan_no_generator import generate_chalan_no
from .models import ChalanMaster, ChalanDetail


class CreateChalanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChalanDetail
        fields = ['id', 'item', 'item_category', 'qty', 'sale_cost',
                  'discountable', 'taxable', 'tax_rate', 'tax_amount',
                  'discount_rate', 'discount_amount', 'gross_amount', 'net_amount',
                  'ref_order_detail', 'ref_purchase_detail', 'remarks'
                  ]
        extra_kwargs = {
            'ref_order_detail': {'required': True},
            'ref_purchase_detail': {'required': True},
        }


class CreateChalanMasterSerializer(serializers.ModelSerializer):
    chalan_details = CreateChalanDetailSerializer(many=True)

    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no', 'status', 'customer', 'discount_scheme',
                  'discount_rate',
                  'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'ref_order_master', 'grand_total', 'remarks', 'chalan_details'
                  ]
        read_only_fields = ['chalan_no', 'status']
        extra_kwargs = {'ref_order_master': {'required': True}}

    def create(self, validated_data):
        created_date_ad = timezone.now()
        created_by = current_user.get_created_by(self.context)
        chalan_details = validated_data.pop('chalan_details')
        # saving order_master status to CHALAN
        order_master = validated_data['ref_order_master']
        order_master.status = 4
        order_master.save()
        chalan_master_db = ChalanMaster.objects.create(
            **validated_data,
            chalan_no=generate_chalan_no(),
            status=1,
            created_date_ad=created_date_ad,
            created_by=created_by
        )
        for chalan_detail in chalan_details:
            chalan_detail_db = ChalanDetail.objects.create(
                **chalan_detail, chalan_master=chalan_master_db,
                created_date_ad=created_date_ad, created_by=created_by
            )
            customer_order_detail = chalan_detail_db.ref_order_detail
            # save chalan packing type codes
            SalePackingTypeCode.objects.filter(
                customer_order_detail=customer_order_detail
            ).update(chalan_detail=chalan_detail_db)
        return chalan_master_db

    def validate(self, data):
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP

        quantize_places = decimal.Decimal(10) ** -2
        # initialize variables to check
        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        chalan_details = data['chalan_details']

        for chalan in chalan_details:
            chalan_details = {}
            key_values = zip(chalan.keys(), chalan.values())
            for key, values in key_values:
                chalan_details[key] = values

            # validation for amount values less than or equal to 0 "Zero"
            if chalan_details['tax_rate'] < 0 or chalan_details['discount_rate'] < 0:
                raise serializers.ValidationError({
                    f'item {chalan_details["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                           ' cannot be less than 0'})

            if chalan_details['qty'] <= 0 or chalan_details['sale_cost'] <= 0:
                raise serializers.ValidationError({
                    f'item {chalan_details["item"].name}': 'values in fields, quantity, sale_cost cannot be less than'
                                                           ' or equals to 0'})
            if chalan_details['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {chalan_details["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = chalan_details['sale_cost'] * chalan_details['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != chalan_details['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {chalan_details["item"].name}': ' gross_amount calculation not valid : should be {}'.format(
                            gross_amount)})
            sub_total += gross_amount
            # validation for discount amount
            if chalan_details['discountable'] is True:
                total_discountable_amount = total_discountable_amount + chalan_details['gross_amount']
                discount_rate = (chalan_details['discount_amount'] *
                                 Decimal('100')) / (chalan_details['sale_cost'] *
                                                    chalan_details['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != chalan_details['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {chalan_details["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + chalan_details['discount_amount']
            elif chalan_details['discountable'] is False and chalan_details['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {chalan_details["item"].name}':
                                                       f'discount_amount {chalan_details["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - chalan_details['discount_amount']
            if chalan_details['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = chalan_details['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != chalan_details['tax_amount']:
                    raise serializers.ValidationError({f'item {chalan_details["item"].name}':
                                                           f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif chalan_details['taxable'] is False:
                if chalan_details['tax_rate'] != 0 or chalan_details['tax_amount'] != 0:
                    raise serializers.ValidationError({f'item {chalan_details["item"].name}':
                                                           "taxable = False, tax_rate and tax_amount should be 0"})
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((chalan_details['sale_cost'] *
                                           chalan_details['qty'] *
                                           chalan_details['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (chalan_details['sale_cost'] *
                                           chalan_details['qty'] *
                                           chalan_details['discount_rate']) / Decimal('100')) *
                          chalan_details['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != chalan_details['net_amount']:
                raise serializers.ValidationError({f'item {chalan_details["item"].name}':
                                                       f'net_amount calculation not valid : should be {net_amount}'})
            grand_total = grand_total + net_amount

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                f'total_discountable_amount calculation {data["total_discountable_amount"]} not valid: should be {total_discountable_amount}'
            )
        # # Adding of additional charge in grand total
        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                f'grand_total calculation {data["grand_total"]} not valid: should be {grand_total}'
            )

        # validation for total_taxable_amount
        if total_taxable_amount != data['total_taxable_amount']:
            raise serializers.ValidationError(
                'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
                                                                                     total_taxable_amount)
            )

        # validation for total_non_taxable_amount
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
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'], total_discount)
            )
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        return data


# ************************** Listing Serializers ********************************


class PackingTypeDetailCodeChalanViewSerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source='packing_type_detail_code.code')

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'code']
        read_only_fields = fields


class PackingTypeCodeChalanViewSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = PackingTypeDetailCodeChalanViewSerializer(many=True)
    code = serializers.ReadOnlyField(source='packing_type_code.code', allow_null=True)
    location_code = serializers.ReadOnlyField(source='packing_type_code.location.code', allow_null=True)
    location = serializers.ReadOnlyField(source='packing_type_code.location.id', allow_null=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'location_code', 'location', 'code',
                  'packing_type_code', 'sale_packing_type_detail_code']
        read_only_fields = fields


class ChalanSummaryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'code']


class ChalanSummaryCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name',
                  'pan_vat_no', 'phone_no',
                  'address']


class ChalanSummaryDiscountScheme(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = ['id', 'name', 'rate']


class ChalanDetailSummarySerializer(serializers.ModelSerializer):
    item = ChalanSummaryItemSerializer(read_only=True)

    chalan_packing_types = PackingTypeCodeChalanViewSerializer(many=True, read_only=True)

    class Meta:
        model = ChalanDetail
        fields = ['id', 'item', 'item_category', 'qty', 'sale_cost',
                  'discountable', 'taxable', 'tax_rate', 'tax_amount',
                  'discount_rate', 'discount_amount', 'gross_amount', 'net_amount',
                  'ref_purchase_detail',
                  'ref_order_detail', 'remarks', 'chalan_packing_types'
                  ]
        read_only_fields = fields


class ChalanMasterSummarySerializer(serializers.ModelSerializer):
    customer = ChalanSummaryCustomerSerializer(read_only=True)
    discount_scheme = ChalanSummaryDiscountScheme(read_only=True)
    chalan_details = ChalanDetailSummarySerializer(many=True, read_only=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no', 'status', 'customer', 'discount_scheme',
                  'discount_rate',
                  'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'ref_order_master', 'grand_total', 'remarks', 'created_date_ad',
                  'created_date_bs', 'created_by', 'created_by_user_name', 'status_display',
                  'chalan_details']


class ListChalanDetailsSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = ChalanDetail
        fields = ['id', 'item', 'item_category', 'qty', 'sale_cost',
                  'discountable', 'taxable', 'tax_rate', 'tax_amount',
                  'discount_rate', 'discount_amount', 'gross_amount', 'net_amount',
                  'ref_order_detail', 'ref_purchase_detail',
                  'item_category_name', 'item_name', 'remarks'
                  ]
        read_only_fields = fields


class ListChalanMasterSerializer(serializers.ModelSerializer):
    customer = ChalanSummaryCustomerSerializer(read_only=True)
    discount_scheme = ChalanSummaryDiscountScheme(read_only=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    order_no = serializers.ReadOnlyField(source='ref_order_master.order_no', allow_null=True)

    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no', 'status', 'customer', 'discount_scheme',
                  'discount_rate',
                  'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'ref_order_master', 'grand_total', 'remarks', 'created_date_ad', 'created_date_bs',
                  'created_by_user_name', 'status_display', 'order_no', 'ref_chalan_master', 'return_dropped'
                  ]
        read_only_fields = fields


class ListChalanMasterReturnedSerializer(serializers.ModelSerializer):
    customer = ChalanSummaryCustomerSerializer(read_only=True)
    discount_scheme = ChalanSummaryDiscountScheme(read_only=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    order_no = serializers.ReadOnlyField(source='ref_order_master.order_no', allow_null=True)
    chalan_no = serializers.ReadOnlyField(source='ref_chalan_master.chalan_no', allow_null=True)
    chalan_return_no = serializers.ReadOnlyField(source='chalan_no')

    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no', 'status', 'customer', 'discount_scheme',
                  'discount_rate',
                  'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'ref_order_master', 'grand_total', 'remarks', 'created_date_ad', 'created_date_bs',
                  'created_by_user_name', 'status_display', 'order_no', 'ref_chalan_master', 'return_dropped',
                  'chalan_return_no'
                  ]
        read_only_fields = fields
