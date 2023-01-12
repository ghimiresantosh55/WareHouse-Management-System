import decimal

from django.utils import timezone
# rest_framework
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from src.item_serialization.unique_item_serials import (generate_packtype_serial, packing_type_detail_code_list)
from src.supplier.models import Supplier
from .models import PurchaseOrderDetail, PurchaseOrderMaster
from .purchase_unique_id_generator import generate_order_no

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


class POReceivedPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        exclude = ["pack_type_code"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class POReceivedPackingTypeCodeSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = POReceivedPackingTypeDetailCodeSerializer(many=True, required=False)
    pack_no = serializers.IntegerField(write_only=True)

    class Meta:
        model = PackingTypeCode
        exclude = ["purchase_order_detail", "purchase_detail"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'code']
        extra_kwargs = {
            'pack_no': {'write_only': True}
        }


# purchase order detail serializer for Write Only purchase_order_view
class ReceivedPurchaseOrderDetailSerializer(serializers.ModelSerializer):
    po_pack_type_codes = POReceivedPackingTypeCodeSerializer(many=True)
    pack_qty = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    sale_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    ref_purchase_order_detail = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrderDetail.objects.filter(purchase_order__order_type=1),
        required=True
    )

    class Meta:
        model = PurchaseOrderDetail
        exclude = ['purchase_order']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'item_category', 'pack_qty']


# purchase order master nested serializer for Write Only purchase_order_view
class ReceivedPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = ReceivedPurchaseOrderDetailSerializer(many=True)
    order_type = serializers.ChoiceField(PurchaseOrderMaster.PURCHASE_ORDER_TYPE, default=3)
    order_no = serializers.CharField(required=False)
    sub_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=False)
    ref_purchase_order = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrderMaster.objects.filter(order_type=1),
                                                            required=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        validated_data['order_no'] = generate_order_no(3)
        date_now = timezone.now()
        purchase_order_details = validated_data.pop('purchase_order_details')
        order_master = PurchaseOrderMaster.objects.create(**validated_data, created_date_ad=date_now)
        for purchase_order_detail in purchase_order_details:
            pack_type_codes = purchase_order_detail.pop('po_pack_type_codes')
            purchase_order_detail_for_serial = PurchaseOrderDetail.objects.create(
                **purchase_order_detail, pack_qty=purchase_order_detail['packing_type_detail'].pack_qty,
                item_category=purchase_order_detail['item'].item_category,
                purchase_order=order_master, created_by=validated_data['created_by'], created_date_ad=date_now
            )

            len_of_pack_type_code = len(pack_type_codes)
            ref_len_pack_type_code = int(
                purchase_order_detail['qty'] / purchase_order_detail['packing_type_detail'].pack_qty)
            if len_of_pack_type_code != ref_len_pack_type_code:
                raise serializers.ValidationError({"message": "pack type codes not enough"})
            for pack_type_code in pack_type_codes:
                pack_type_detail_codes = []
                if purchase_order_detail['item'].is_serializable is True:
                    pack_type_detail_codes = pack_type_code.pop('pack_type_detail_codes')

                code = generate_packtype_serial()
                pack_type = PackingTypeCode.objects.create(
                    code=code,
                    purchase_order_detail=purchase_order_detail_for_serial,
                    created_by=validated_data['created_by'],
                    created_date_ad=date_now,
                    qty=purchase_order_detail['packing_type_detail'].pack_qty
                )
                if purchase_order_detail['item'].is_serializable is True:
                    if pack_type_detail_codes:
                        if len(pack_type_detail_codes) != int(purchase_order_detail['packing_type_detail'].pack_qty):
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
                        pack_qty = int(purchase_order_detail['packing_type_detail'].pack_qty)

                        pack_type_detail_codes_data = packing_type_detail_code_list(pack_qty=pack_qty,
                                                                                    pack_type_code=pack_type.id,
                                                                                    created_by=validated_data[
                                                                                        'created_by'].id,
                                                                                    created_date_ad=date_now)
                        PackingTypeDetailCode.objects.bulk_create(
                            pack_type_detail_codes_data
                        )
        return order_master

    # def validate(self, attrs):
    #     pass
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
    #     purchase_order_details = data['purchase_order_details']
    #     for purchase_order in purchase_order_details:

    #         purchase_order_detail = {}
    #         key_values = zip(purchase_order.keys(), purchase_order.values())
    #         for key, values in key_values:
    #             purchase_order_detail[key] = values

    #         # Validation for ref_purchase_order_detail  quantity should not be greater than order_qty
    #         # if "ref_purchase_order_detail" in purchase_order_detail:
    #         #     if purchase_order_detail['ref_purchase_order_detail'] is not None:
    #         #         # print(purchase_order_detail)
    #         #         # print(purchase_order)
    #         #         reference_qty = purchase_order_detail['ref_purchase_order_detail'].qty
    #         #         # print( purchase_order_detail['ref_purchase_order_detail'].qty) # approved qty
    #         #         # print(purchase_order_detail['qty']) # order qty
    #         #         if reference_qty < purchase_order_detail['qty']: # 
    #         #             raise serializer.ValidationError({ f'item {purchase_order_detail["item"].name}': f' Approved quantity :{purchase_order_detail["qty"]} should less than or equal to order quantity:{reference_qty} '})

    #         # validation for amount values less than or equal to 0 "Zero"
    #         if purchase_order_detail['tax_rate'] < 0 or purchase_order_detail['discount_rate'] < 0 or \
    #                 purchase_order_detail['sale_cost'] < 0:
    #             raise serializer.ValidationError({
    #                 f'item {purchase_order_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
    #                                                               ' cannot be less than 0'})

    #         if purchase_order_detail['purchase_cost'] <= 0 or purchase_order_detail['qty'] <= 0:
    #             raise serializer.ValidationError({
    #                 f'item {purchase_order_detail["item"].name}': 'values in fields, purchase_cost and quantity cannot be less than'
    #                                                               ' or equals to 0'})
    #         if purchase_order_detail['discount_rate'] > 100:
    #             raise serializer.ValidationError(
    #                 {f'item {purchase_order_detail["item"].name}': 'Discount rate can not be greater than 100.'})

    #         # validation for gross_amount
    #         gross_amount = purchase_order_detail['purchase_cost'] * purchase_order_detail['qty']
    #         gross_amount = gross_amount.quantize(quantize_places)
    #         if gross_amount != purchase_order_detail['gross_amount']:
    #             raise serializer.ValidationError(
    #                 {
    #                     f'item {purchase_order_detail["item"].name}': f'gross_amount calculation not valid, should be {gross_amount}'})
    #         sub_total = sub_total + gross_amount

    #         # validation for discount amount
    #         if purchase_order_detail['discountable'] is True:
    #             total_discountable_amount = total_discountable_amount + purchase_order_detail['gross_amount']
    #             discount_rate = (purchase_order_detail['discount_amount'] *
    #                              Decimal('100')) / (purchase_order_detail['purchase_cost'] *
    #                                                 purchase_order_detail['qty'])
    #             discount_rate = discount_rate.quantize(quantize_places)
    #             if discount_rate != purchase_order_detail['discount_rate']:
    #                 raise serializer.ValidationError(
    #                     {
    #                         f'item {purchase_order_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
    #             total_discount = total_discount + purchase_order_detail['discount_amount']
    #         elif purchase_order_detail['discountable'] is False and purchase_order_detail['discount_amount'] > 0:
    #             raise serializer.ValidationError({f'item {purchase_order_detail["item"].name}':
    #                                                    f'discount_amount {purchase_order_detail["discount_amount"]} can not be '
    #                                                    f'given to item with discountable = False'})

    #         # validation for tax amount
    #         probable_taxable_amount = gross_amount - purchase_order_detail['discount_amount']
    #         if purchase_order_detail['taxable'] is True:
    #             total_taxable_amount = total_taxable_amount + probable_taxable_amount
    #             tax_amount = purchase_order_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
    #             tax_amount = tax_amount.quantize(quantize_places)
    #             if tax_amount != purchase_order_detail['tax_amount']:
    #                 raise serializer.ValidationError({f'item {purchase_order_detail["item"].name}':
    #                                                        f'tax_amount calculation not valid : should be {tax_amount}'})
    #             total_tax = total_tax + tax_amount
    #         elif purchase_order_detail['taxable'] is False:
    #             total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

    #         # validation for net_amount
    #         net_amount = (gross_amount - ((
    #                                        purchase_order_detail['discount_amount']) )) + \
    #                      ((gross_amount - (
    #                                        purchase_order_detail['discount_amount'])) *
    #                       purchase_order_detail['tax_rate'] / Decimal('100'))

    #         net_amount = net_amount.quantize(quantize_places)
    #         if net_amount != purchase_order_detail['net_amount']:
    #             raise serializer.ValidationError(
    #                 {
    #                     f'item {purchase_order_detail["item"].name}': f'net_amount calculation not valid : should be {net_amount}'})
    #         grand_total = grand_total + net_amount

    #     # validation for total_discountable_amount
    #     if total_discountable_amount != data['total_discountable_amount']:
    #         raise serializer.ValidationError(
    #             {'total_discountable_amount':
    #                  f'total_discountable_amount calculation {data["total_discountable_amount"]} not valid: should be {total_discountable_amount}'}
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

    #     # validation for total_discount 
    #     if total_discount != data['total_discount']:
    #         raise serializer.ValidationError(
    #             'total_discount calculation {} not valid: should be {}'.format(data['total_discount'], total_discount)
    #         )

    #     # validation for total_tax
    #     if total_tax != data['total_tax']:
    #         raise serializer.ValidationError(
    #             'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
    #         )

    #     # validation for grand_total
    #     if grand_total != data['grand_total']:
    #         raise serializer.ValidationError(
    #             'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
    #         )

    #     return data


class POReceivedPackingTypeDetailCodeGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        fields = ['id', "code"]
        read_only_fields = fields


class POReceivedPackingTypeCodeGetSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = POReceivedPackingTypeDetailCodeGetSerializer(many=True, required=False)

    class Meta:
        model = PackingTypeCode
        fields = ['id', "pack_type_detail_codes", "code", 'location']
        read_only_fields = fields


# purchase order detail serializer for Write Only purchase_order_view
class PurchaseOrderDetailReceivedGetSerializer(serializers.ModelSerializer):
    po_pack_type_codes = POReceivedPackingTypeCodeGetSerializer(many=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)

    class Meta:
        model = PurchaseOrderDetail
        fields = ['po_pack_type_codes', 'item_category_name', 'item_name',
                  'packing_type_name', 'id', 'item', 'item_category', 'sale_cost', 'purchase_cost',
                  'qty', 'pack_qty', 'packing_type', 'packing_type_detail', 'tax_rate', 'tax_amount',
                  'discount_rate', 'discount_amount', 'gross_amount', 'net_amount']
        read_only_fields = fields
