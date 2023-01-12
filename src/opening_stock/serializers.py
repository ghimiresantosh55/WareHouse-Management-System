from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.custom_lib.functions import current_user
from src.custom_lib.functions import fiscal_year
# custom lib
from src.custom_lib.functions.validators import purchase_opening_stock_qty_patch_validator
from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from src.item_serialization.unique_item_serials import (packing_type_detail_code_list,
                                                        generate_packtype_serial)
# custom models
from src.purchase.models import PurchaseMaster, PurchaseDetail
from src.purchase.purchase_unique_id_generator import generate_purchase_no, generate_batch_no
from .listing_apis.listing_serializers import OpeningStockItemListSerializer, \
    OpeningStockPackingTypeDetailListSerializer, OpeningStockPackingTypeListSerializer


class OpeningStockSerializer(serializers.ModelSerializer):
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    created_by_first_name = serializers.ReadOnlyField(source='created_by.first_name', allow_null=True)
    dropped = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def get_dropped(self, instance):
        purchase_details = PurchaseDetail.objects.filter(purchase=instance)
        for purchase_detail in purchase_details:
            pu_pack_type_codes = PackingTypeCode.objects.filter(
                purchase_detail=purchase_detail,
                ref_packing_type_code__isnull=True
            )
            for pack_type_code in pu_pack_type_codes:
                if pack_type_code.location is None:
                    return False
        return True

    def get_department(self, instance):
        return {
            "id": instance.department.id,
            "name": instance.department.name,
            "code": instance.department.code,
        }

class OpeningStockDetailSerializer(serializers.ModelSerializer):
    item = OpeningStockItemListSerializer(read_only=True)
    packing_type = OpeningStockPackingTypeListSerializer(read_only=True)
    packing_type_detail = OpeningStockPackingTypeDetailListSerializer(read_only=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = "__all__"


class OpeningStockSummarySerializer(serializers.ModelSerializer):
    purchase_details = OpeningStockDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"


class SavePurchaseOpeningStockPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        exclude = ["pack_type_code"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SavePurchaseOpeningStockPackingTypeCodeSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = SavePurchaseOpeningStockPackingTypeDetailCodeSerializer(
        many=True, required=False
    )
    pack_no = serializers.IntegerField(write_only=True)

    class Meta:
        model = PackingTypeCode
        exclude = ["purchase_order_detail", "purchase_detail"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'code']
        extra_kwargs = {
            'pack_no': {'write_only': True}
        }


class SavePurchaseOpeningStockDetailSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = SavePurchaseOpeningStockPackingTypeCodeSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'item', 'item_category', 'purchase_cost', 'sale_cost',
                  'qty', 'pack_qty', 'packing_type', 'packing_type_detail',
                  'taxable', 'tax_rate', 'tax_amount', 'discountable', 'expirable',
                  'discount_rate', 'discount_amount', 'discount_amount', 'gross_amount',
                  'gross_amount', 'net_amount', 'expiry_date_ad', 'expiry_date_bs',
                  'batch_no', 'item_name', 'item_category_name', 'created_by_user_name',
                  'pu_pack_type_codes']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'batch_no']


class SaveOpeningStockSerializer(serializers.ModelSerializer):
    purchase_details = SavePurchaseOpeningStockDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'purchase_type', 'pay_type',
                  'sub_total', 'total_discount', 'discount_rate', 'discount_scheme',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'total_tax', 'grand_total', 'supplier', 'bill_no',
                  'bill_date_ad', 'bill_date_bs', 'chalan_no', 'remarks', 'department',
                  'purchase_details', 'created_by_user_name']
        read_only_fields = ['created_by', 'created_date_ad', 'pay_type',
                            'created_date_bs', 'purchase_no', 'purchase_type',
                            'bill_data_bs']

        extra_kwargs = {'department': {'required': True}}

    def create(self, validated_data):
        created_date_ad = timezone.now()
        created_by = current_user.get_created_by(self.context)
        purchase_no = generate_purchase_no(purchase_type=3)
        purchase_details = validated_data.pop('purchase_details')
        purchase_type = 3  # 3 => OpeningStock

        # fiscal sessions
        fiscal_year_ad_short = fiscal_year.get_fiscal_year_code_ad()
        fiscal_year_bs_short = fiscal_year.get_fiscal_year_code_bs()
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
            pay_type=1,
            fiscal_session_ad=fiscal_session_ad, fiscal_session_bs=fiscal_session_bs
        )
        if not purchase_details:
            raise serializers.ValidationError({'purchase_details': 'please provide purchase details'})
        for purchase_detail in purchase_details:
            pack_type_codes = purchase_detail.pop('pu_pack_type_codes')
            batch_no = generate_batch_no()
            purchase_detail_db = PurchaseDetail.objects.create(
                **purchase_detail, purchase=purchase_master, batch_no=batch_no,
                created_date_ad=created_date_ad,
                created_by=created_by
            )
            len_of_pack_type_code = len(pack_type_codes)
            ref_len_pack_type_code = int(
                purchase_detail['qty'] / purchase_detail['packing_type_detail'].pack_qty)
            if len_of_pack_type_code != ref_len_pack_type_code:
                raise serializers.ValidationError({"message": "pack type codes not enough"})
            for pack_type_code in pack_type_codes:
                pack_type_detail_codes = pack_type_code.pop('pack_type_detail_codes')

                code = generate_packtype_serial()
                pack_type = PackingTypeCode.objects.create(
                    code=code,
                    purchase_detail=purchase_detail_db,
                    created_by=created_by,
                    created_date_ad=created_date_ad
                )
                if pack_type_detail_codes:
                    if len(pack_type_detail_codes) != int(purchase_detail['packing_type_detail'].pack_qty):
                        raise serializers.ValidationError({"message": "packing type detail codes count does nto match"})
                    for pack_type_detail_code in pack_type_detail_codes:
                        PackingTypeDetailCode.objects.create(
                            code=pack_type_detail_code['code'],
                            pack_type_code=pack_type,
                            created_by=created_by,
                            created_date_ad=created_date_ad
                        )
                else:
                    pack_qty = int(purchase_detail['packing_type_detail'].pack_qty)

                    pack_type_detail_codes_data = packing_type_detail_code_list(pack_qty=pack_qty,
                                                                                pack_type_code=pack_type.id,
                                                                                created_by=created_by.id,
                                                                                created_date_ad=created_date_ad)
                    PackingTypeDetailCode.objects.bulk_create(
                        pack_type_detail_codes_data
                    )
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
    #     grand_total = Decimal('0.00')
    #     purchase_details = data['purchase_details']
    #     for purchase in purchase_details:
    #         purchase_detail = {}
    #         key_values = zip(purchase.keys(), purchase.values())
    #         for key, values in key_values:
    #             purchase_detail[key] = values
    #         # validation for amount values less than or equal to 0 "Zero"
    #         if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0 or \
    #                 purchase_detail['sale_cost'] < 0:
    #             raise serializer.ValidationError({
    #                 f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
    #                                                         ' cannot be less than 0'})
    #
    #         if purchase_detail['purchase_cost'] < 0:
    #             raise serializer.ValidationError({
    #                 f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost cannot be less than 0'})
    #         if purchase_detail['qty'] <= 0:
    #             raise serializer.ValidationError({
    #                 f'item {purchase_detail["item"].name}': 'values in fields, quantity cannot be less than'
    #                                                         ' or equals to 0'})
    #         if purchase_detail['discount_rate'] > 100:
    #             raise serializer.ValidationError(
    #                 {f'item {purchase_detail["item"].name}': 'Discount rate can not be greater than 100.'})
    #
    #         # validation for gross_amount
    #         gross_amount = purchase_detail['purchase_cost'] * purchase_detail['qty']
    #         gross_amount = gross_amount.quantize(quantize_places)
    #         if gross_amount != purchase_detail['gross_amount']:
    #             raise serializer.ValidationError(
    #                 {
    #                     f'item {purchase_detail["item"].name}': f'gross_amount calculation not valid : should be {gross_amount}'})
    #         sub_total = sub_total + gross_amount
    #
    #         # validation for discount amount
    #         if purchase_detail['discountable'] is True:
    #             total_discountable_amount = total_discountable_amount + purchase_detail['gross_amount']
    #             discount_rate = (purchase_detail['discount_amount'] *
    #                              Decimal('100')) / (purchase_detail['purchase_cost'] *
    #                                                 purchase_detail['qty'])
    #             discount_rate = discount_rate.quantize(quantize_places)
    #             if discount_rate != purchase_detail['discount_rate']:
    #                 raise serializer.ValidationError(
    #                     {
    #                         f'item {purchase_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
    #             total_discount = total_discount + purchase_detail['discount_amount']
    #         elif purchase_detail['discountable'] is False and purchase_detail['discount_amount'] > 0:
    #             raise serializer.ValidationError({f'item {purchase_detail["item"].name}':
    #                                                    f'discount_amount {purchase_detail["discount_amount"]} can not be '
    #                                                    f'given to item with discountable = False'})
    #
    #         # validation for tax amount
    #         probable_taxable_amount = gross_amount - purchase_detail['discount_amount']
    #         if purchase_detail['taxable'] is True:
    #             total_taxable_amount = total_taxable_amount + probable_taxable_amount
    #             tax_amount = purchase_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
    #             tax_amount = tax_amount.quantize(quantize_places)
    #             if tax_amount != purchase_detail['tax_amount']:
    #                 raise serializer.ValidationError(
    #                     {
    #                         f'item {purchase_detail["item"].name}': f'tax_amount calculation not valid : should be {tax_amount}'})
    #             total_tax = total_tax + tax_amount
    #         elif purchase_detail['taxable'] is False:
    #             total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount
    #
    #         # validation for net_amount
    #         net_amount = (gross_amount - ((purchase_detail['purchase_cost'] *
    #                                        purchase_detail['qty'] *
    #                                        purchase_detail['discount_rate']) / Decimal('100'))) + \
    #                      ((gross_amount - (purchase_detail['purchase_cost'] *
    #                                        purchase_detail['qty'] *
    #                                        purchase_detail['discount_rate']) / Decimal('100')) *
    #                       purchase_detail['tax_rate'] / Decimal('100'))
    #         net_amount = net_amount.quantize(quantize_places)
    #         if net_amount != purchase_detail['net_amount']:
    #             raise serializer.ValidationError({f'item {purchase_detail["item"].name}':
    #                 'net_amount calculation not valid : should be {}'.format(
    #                     net_amount)})
    #         grand_total = grand_total + net_amount
    #
    #     # validation for purchase in CREDIT with no supplier
    #     if data['pay_type'] == 2 and data['supplier'] == '':
    #         raise serializer.ValidationError('Cannot perform purchase in CREDIT with no supplier')
    #
    #     # validation for total_discountable_amount
    #     if total_discountable_amount != data['total_discountable_amount']:
    #         raise serializer.ValidationError(
    #             'total_discountable_amount calculation {} not valid: should be {}'.format(
    #                 data['total_discountable_amount'], total_discountable_amount)
    #         )
    #
    #     # validation for total_taxable_amount
    #     if total_taxable_amount != data['total_taxable_amount']:
    #         raise serializer.ValidationError(
    #             'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
    #                                                                                  total_taxable_amount)
    #         )
    #
    #     # validation for total_nontaxable_amount
    #     if total_nontaxable_amount != data['total_non_taxable_amount']:
    #         raise serializer.ValidationError(
    #             'total_non_taxable_amount calculation {} not valid: should be {}'.format(
    #                 data['total_non_taxable_amount'],
    #                 total_nontaxable_amount)
    #         )
    #
    #     # check subtotal , total discount , total tax and grand total
    #     if sub_total != data['sub_total']:
    #         raise serializer.ValidationError(
    #             'sub_total calculation not valid: should be {}'.format(sub_total)
    #         )
    #
    #     if total_discount != data['total_discount']:
    #         raise serializer.ValidationError(
    #             'total_discount calculation {} not valid: should be {}'.format(data['total_discount'],
    #                                                                            total_discount)
    #         )
    #     if total_tax != data['total_tax']:
    #         raise serializer.ValidationError(
    #             'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
    #         )
    #
    #     # grand_total = grand_total + add_charge
    #     if grand_total != data['grand_total']:
    #         raise serializer.ValidationError(
    #             'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
    #         )
    #
    #     return data
    #


class UpdateOpeningStockSerializer(serializers.ModelSerializer):
    purchase_details = SavePurchaseOpeningStockDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def update(self, instance, validated_data):
        purchase_details_data = validated_data.pop('purchase_details')

        purchase_details = (instance.purchase_details).all()
        purchase_details = list(purchase_details)

        # children data in purchase_details must be equal
        if len(purchase_details) != len(purchase_details_data):
            raise serializers.ValidationError("To perform patch operation you must call all purcahse detail")

        instance.sub_total = validated_data.get('sub_total', instance.sub_total)
        instance.total_discount = validated_data.get('total_discount', instance.total_discount)
        instance.discount_rate = validated_data.get('discount_rate', instance.discount_rate)
        instance.discount_scheme = validated_data.get('discount_scheme', instance.discount_scheme)
        instance.total_discountable_amount = validated_data.get('total_discountable_amount',
                                                                instance.total_discountable_amount)
        instance.total_taxable_amount = validated_data.get('total_taxable_amount', instance.total_taxable_amount)
        instance.total_non_taxable_amount = validated_data.get('total_non_taxable_amount',
                                                               instance.total_non_taxable_amount)
        instance.total_tax = validated_data.get('total_tax', instance.total_tax)
        instance.grand_total = validated_data.get('grand_total', instance.grand_total)
        instance.remarks = validated_data.get('remarks', instance.remarks)

        for purchase_detail_data in purchase_details_data:
            purchase_detail = purchase_details.pop(0)
            # checking of quantity while performing patch operation
            purchase_opening_stock_qty_patch_validator(purchase_detail.id, purchase_detail_data['qty'])
            purchase_detail.id = purchase_detail_data.get('id', purchase_detail.id)
            purchase_detail.item = purchase_detail_data.get('item', purchase_detail.item)
            purchase_detail.item_category = purchase_detail_data.get('item_category', purchase_detail.item_category)
            purchase_detail.purchase_cost = purchase_detail_data.get('purchase_cost', purchase_detail.purchase_cost)
            purchase_detail.sale_cost = purchase_detail_data.get('sale_cost', purchase_detail.sale_cost)
            purchase_detail.qty = purchase_detail_data.get('qty', purchase_detail.qty)
            purchase_detail.taxable = purchase_detail_data.get('taxable', purchase_detail.taxable)
            purchase_detail.tax_rate = purchase_detail_data.get('tax_rate', purchase_detail.tax_rate)
            purchase_detail.tax_amount = purchase_detail_data.get('tax_amount', purchase_detail.tax_amount)
            purchase_detail.discountable = purchase_detail_data.get('discountable', purchase_detail.discountable)
            purchase_detail.expirable = purchase_detail_data.get('expirable', purchase_detail.expirable)
            purchase_detail.discount_rate = purchase_detail_data.get('discount_rate', purchase_detail.discount_rate)
            purchase_detail.discount_amount = purchase_detail_data.get('discount_amount',
                                                                       purchase_detail.discount_amount)
            purchase_detail.gross_amount = purchase_detail_data.get('gross_amount', purchase_detail.gross_amount)
            purchase_detail.net_amount = purchase_detail_data.get('net_amount', purchase_detail.net_amount)
            purchase_detail.expiry_date_ad = purchase_detail_data.get('expiry_date_ad', purchase_detail.expiry_date_ad)
            purchase_detail.expiry_date_bs = purchase_detail_data.get('expiry_date_bs', purchase_detail.expiry_date_bs)
            purchase_detail.batch_no = purchase_detail_data.get('batch_no', purchase_detail.batch_no)
            purchase_detail.save()

        instance.save()
        return instance

    def validate(self, data):
        # changing into decimal form with 2 digit after point 
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

            # tax_rate, discount and sale_cost cannot be less than  0 but can be 0
            if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0 or \
                    purchase_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                            ' cannot be less than 0'})

            # purchase cost can be 0 but cannot be less than 0
            if purchase_detail['purchase_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost cannot be less than 0'})

            # qty cannot be less than or is equal to 0. Must have atleast 1 qty.
            if purchase_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, quantity cannot be less than'
                                                            ' or equals to 0'})

            # discount_rate cannot be greater than 100
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
            net_amount = (gross_amount - ((purchase_detail['purchase_cost'] *
                                           purchase_detail['qty'] *
                                           purchase_detail['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (purchase_detail['purchase_cost'] *
                                           purchase_detail['qty'] *
                                           purchase_detail['discount_rate']) / Decimal('100')) *
                          purchase_detail['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_detail['net_amount']:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                    'net_amount calculation not valid : should be {}'.format(
                        net_amount)})
            grand_total = grand_total + net_amount

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

        # validation of discount
        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'],
                                                                               total_discount)
            )

        # validation of tax
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
            )

        # for validation of purchase_type 
        if data['purchase_type'] != 3:
            raise serializers.ValidationError('purcahse_type must be 3')

        return data
