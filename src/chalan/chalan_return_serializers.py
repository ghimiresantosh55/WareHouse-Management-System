import decimal
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from .chalan_no_generator import generate_chalan_return_no
from .models import ChalanDetail
from .models import ChalanMaster


# ****************************** Create Serializers **********************************
class ReturnChalanPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'ref_sale_packing_type_detail_code']
        extra_kwargs = {
            'ref_sale_packing_type_detail_code': {'required': True},
        }


class ReturnChalanPackingTypeCodeSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = ReturnChalanPackingTypeDetailCodeSerializer(many=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'packing_type_code', 'customer_order_detail',
                  'ref_sale_packing_type_code',
                  'sale_packing_type_detail_code']
        extra_kwargs = {
            'ref_sale_packing_type_code': {'required': True},
            'customer_order_detail': {'required': True},
        }


class ReturnChalanDetailSerializer(serializers.ModelSerializer):
    chalan_packing_types = ReturnChalanPackingTypeCodeSerializer(many=True)

    class Meta:
        model = ChalanDetail
        fields = ['id', 'item', 'item_category', 'qty', 'sale_cost',
                  'discountable', 'taxable', 'tax_rate', 'tax_amount',
                  'discount_rate', 'discount_amount', 'gross_amount', 'net_amount',
                  'ref_order_detail', 'ref_purchase_detail', 'remarks', 'ref_chalan_detail',
                  'chalan_packing_types'
                  ]
        extra_kwargs = {
            'order_detail': {'required': True},
            'ref_chalan_detail': {'required': True},
        }


class ReturnChalanMasterSerializer(serializers.ModelSerializer):
    chalan_details = ReturnChalanDetailSerializer(many=True)

    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no', 'status', 'customer', 'discount_scheme',
                  'discount_rate',
                  'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'ref_order_master', 'grand_total', 'remarks', 'chalan_details',
                  'ref_chalan_master'

                  ]
        read_only_fields = ['chalan_no', 'status']
        extra_kwargs = {
            'order_master': {'required': True},
            'ref_chalan_master': {'required': True},
        }

    def create(self, validated_data):
        created_date_ad = timezone.now()
        created_by = current_user.get_created_by(self.context)
        chalan_details = validated_data.pop('chalan_details')
        validated_data['return_dropped'] = False
        chalan_master_db = ChalanMaster.objects.create(
            **validated_data,
            chalan_no=generate_chalan_return_no(),
            status=3,
            created_date_ad=created_date_ad,
            created_by=created_by
        )
        for chalan_detail in chalan_details:
            pk_type_codes = chalan_detail.pop('chalan_packing_types')
            chalan_detail_db = ChalanDetail.objects.create(
                **chalan_detail, chalan_master=chalan_master_db,
                created_date_ad=created_date_ad, created_by=created_by
            )
            for pk_type_code in pk_type_codes:
                packing_type_detail_code = pk_type_code.pop("sale_packing_type_detail_code")
                chalan_pk_code = SalePackingTypeCode.objects.create(
                    **pk_type_code,
                    chalan_detail=chalan_detail_db
                )
                for pk_type_detail_code in packing_type_detail_code:
                    SalePackingTypeDetailCode.objects.create(
                        **pk_type_detail_code,
                        sale_packing_type_code=chalan_pk_code
                    )

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
        if data['ref_chalan_master'].status != 1:
            raise serializers.ValidationError({
                "message": "Chalan status must be CHALAN"
            })
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


class ChalanReturnDropSerializer(serializers.Serializer):
    chalan_master = serializers.PrimaryKeyRelatedField(
        queryset=ChalanMaster.objects.filter(return_dropped=False, status=3)
    )
    chalan_serial_nos = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=SalePackingTypeDetailCode.objects.filter(
            sale_packing_type_code__chalan_detail__chalan_master__return_dropped=False

        ).annotate(chalan_master=F('sale_packing_type_code__chalan_detail__chalan_master_id')).distinct()
    ))

    def create(self, validated_data):
        chalan_master = validated_data['chalan_master']
        chalan_serial_nos = validated_data['chalan_serial_nos']
        chalan_details = ChalanDetail.objects.filter(
            chalan_master=chalan_master
        ).aggregate(total_qty=Sum('qty'))
        if len(chalan_serial_nos) != chalan_details['total_qty']:
            raise serializers.ValidationError({"error": "please scan all/only serial nos for this chalan return"})
        for chalan_serial_no in chalan_serial_nos:

            if chalan_serial_no.chalan_master != chalan_master.id:
                raise serializers.ValidationError(
                    {"error": f"serial no {chalan_serial_no.chalan_master} does not match with this chalan return"})

        chalan_master.return_dropped = True
        chalan_master.save()
        return validated_data


class ChalanReturnInfoPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source="packing_type_detail_code.code", allow_null=True)

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'code']
        read_only_fields = fields


class ChalanReturnInfoPackingTypeCodeSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = ChalanReturnInfoPackingTypeDetailCodeSerializer(many=True)
    code = serializers.ReadOnlyField(source="packing_type_code.code", allow_null=True)
    location_code = serializers.ReadOnlyField(source="packing_type_code.location.code", allow_null=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'packing_type_code', 'code',
                  'sale_packing_type_detail_code', 'customer_order_detail', 'location_code']
        read_only_fields = fields


class ChalanDetailReturnInfoSerializer(serializers.ModelSerializer):
    chalan_packing_types = ChalanReturnInfoPackingTypeCodeSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')
    code_name = serializers.ReadOnlyField(source='item.code')
    unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    batch_no = serializers.ReadOnlyField(source='ref_purchase_detail.batch_no')

    class Meta:
        model = ChalanDetail
        exclude = ['created_date_ad', 'created_date_bs', 'ref_chalan_detail', 'created_by']
