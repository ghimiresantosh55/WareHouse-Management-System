# rest_framework
import decimal
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import (AdditionalChargeType, DiscountScheme, PaymentMode)
from src.custom_lib.functions import current_user
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail
from src.item.serializers import PackingTypeSerializer
from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from src.supplier.models import Supplier
# Models from purchase app
from .models import (PurchaseAdditionalCharge, PurchaseDetail, PurchaseDocument, PurchaseMaster,
                     PurchaseOrderDetail, PurchaseOrderMaster, PurchasePaymentDetail, PurchaseOrderDocument)

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


class PurchaseOrderMasterDocumentListSerializer(serializers.ModelSerializer):
    document_type_name = serializers.ReadOnlyField(source='document_type.name')

    class Meta:
        model = PurchaseOrderDocument
        fields = ['id', 'title', 'document_type', 'document_url',
                  'remarks', 'created_date_ad', 'created_date_bs',
                  'document_type_name']
        read_only_fields = fields


# purchase order master serializer for read only purchase_order_view
class PurchaseOrderMasterSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    department_name = serializers.ReadOnlyField(source='department.name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)
    purchase_order_documents = PurchaseOrderMasterDocumentListSerializer(many=True, read_only=True)
    purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.ref_purchase_order.order_no',
                                                  allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['order_type_display', 'created_by', 'created_date_ad', 'created_date_bs']


# Purchase order for get-orders purchase_order_view
class UnVerifiedPurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['order_type_display', 'created_by', 'created_date_ad', 'created_date_bs']


# purchase order master serializer for read only purchase_order_view
class PurchaseOrderMasterReceivedSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)
    verified = serializers.SerializerMethodField()
    dropped = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['order_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def get_verified(self, instance):
        if instance.purchase_order_details.filter(self_purchase_order_detail__isnull=True).exists():
            return False
        return True

    def get_dropped(self, instance):
        purchase_order_details = PurchaseOrderDetail.objects.filter(purchase_order=instance)
        for purchase_order_detail in purchase_order_details:
            pack_codes = PackingTypeCode.objects.filter(
                purchase_order_detail=purchase_order_detail,
                ref_packing_type_code__isnull=True
            )
            for pack_code in pack_codes:
                if pack_code.location is None:
                    return False
        return True

    def get_supplier(self, instance):
        supplier = instance.supplier
        if supplier:
            try:
                country_name = instance.supplier.country.name
            except AttributeError:
                country_name = None

            return {
                "id": instance.supplier.id,
                "name": instance.supplier.name,
                "address": instance.supplier.address,
                "country": country_name,
            }
        return None
    def get_department(self, instance):


            return {
                "id": instance.department.id,
                "name": instance.department.name,
                "code": instance.department.code,

            }



# purchase order detail serializer for read only purchase_order_view
class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)

    class Meta:
        model = PurchaseOrderDetail
        fields = "__all__"
        read_only_fields = ['item_name', 'item_category_name', 'created_by', 'created_date_ad', 'created_date_bs']


class GetPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)
    item_name = serializers.ReadOnlyField(source="item.name", allow_null=True)

    class Meta:
        model = PackingTypeDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class PackingTypeCodePurchaseViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeCode
        fields = ['id', 'code', 'location']


# purchase order detail serializer for Read Only purchase_order_view
class GetPurchaseOrderDetailSerializer(serializers.ModelSerializer):
    po_pack_type_codes = PackingTypeCodePurchaseViewSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_code = serializers.ReadOnlyField(source='item.code', allow_null=True)
    item_basic_info = serializers.ReadOnlyField(source='item.basic_info', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    item_harmonic_code = serializers.ReadOnlyField(source='item.harmonic_code', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    packing_type_detail_item_unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    item_unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    order_no = serializers.ReadOnlyField(source='purchase_order.order_no')
    expirable = serializers.ReadOnlyField(source='item.expirable')

    packing_type_details_itemwise = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderDetail
        exclude = ['purchase_order']
        read_only_fields = ['created_date_ad', 'created_by', 'created_date_bs']

    @staticmethod
    def get_packing_type_details_itemwise(purchase_detail):
        # print(purchase_detail.item.id)
        try:
            packing_type_details_itemwise = PackingTypeDetail.objects.filter(item=purchase_detail.item.id);
            # print(packing_type_details_itemwise)
            packing_serializer = GetPackingTypeDetailSerializer(packing_type_details_itemwise, many=True)
            # print(packing_serializer.data)
            return packing_serializer.data
        except:
            return None

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order_detail', 'item_name', 'item_category_name'}
        data = super().to_representation(instance)
        packing_type = PackingType.objects.get(id=int(data.pop('packing_type')))
        packing_serializer = PackingTypeSerializer(packing_type)
        data['packing_type'] = packing_serializer.data
        packing_type_detail = PackingTypeDetail.objects.get(id=int(data.pop('packing_type_detail')))
        packing_detail_serializer = GetPackingTypeDetailSerializer(packing_type_detail)
        data['packing_type_detail'] = packing_detail_serializer.data

        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class DiscountSchemeGetOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = ['id', 'name', 'rate']
        read_only_fields = fields


# Purchase order for get-orders purchase_order_view
class GetPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = GetPurchaseOrderDetailSerializer(many=True)
    discount_scheme = DiscountSchemeGetOrdersSerializer(read_only=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    supplier_address = serializers.ReadOnlyField(source='supplier.address', allow_null=True)
    supplier_country_name = serializers.ReadOnlyField(source='supplier.country.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['supplier_name', 'order_type_display', 'created_by', 'created_date_ad',
                            'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order', 'supplier_name', 'created_by_user_name', 'discount_scheme_name',
                     'ref_purchase_order_no'}
        data = super().to_representation(instance)

        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# purchase order detail serializer for Write Only purchase_order_view
class SavePurchaseOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDetail
        exclude = ['purchase_order']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'item_category']

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class SavePurchaseOrderDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDocument
        exclude = ['purchase_order']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# purchase order master nested serializer for Write Only purchase_order_view
class SavePurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = SavePurchaseOrderDetailSerializer(many=True)
    purchase_order_documents = SavePurchaseOrderDocumentsSerializer(many=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']
        extra_kwargs = {
            "department": {"required": True}
        }

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order'}
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
        purchase_order_details = validated_data.pop('purchase_order_details')
        purchase_order_documents = validated_data.pop('purchase_order_documents')
        order_master = PurchaseOrderMaster.objects.create(**validated_data, created_date_ad=date_now)
        for purchase_order_detail in purchase_order_details:
            PurchaseOrderDetail.objects.create(
                **purchase_order_detail, item_category=purchase_order_detail['item'].item_category,
                purchase_order=order_master, created_by=validated_data['created_by'], created_date_ad=date_now
            )
        for purchase_order_document in purchase_order_documents:
            PurchaseOrderDocument.objects.create(
                **purchase_order_document, purchase_order=order_master,
                created_by=validated_data['created_by'], created_date_ad=date_now
            )
        return order_master

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
        purchase_order_details = data['purchase_order_details']
        for purchase_order in purchase_order_details:

            purchase_order_detail = {}
            key_values = zip(purchase_order.keys(), purchase_order.values())
            for key, values in key_values:
                purchase_order_detail[key] = values

            # Validation for ref_purchase_order_detail  quantity should not be greater than order_qty
            if "ref_purchase_order_detail" in purchase_order_detail:
                if purchase_order_detail['ref_purchase_order_detail'] is not None:
                    # print(purchase_order_detail)
                    # print(purchase_order)
                    reference_qty = purchase_order_detail['ref_purchase_order_detail'].qty
                    # print( purchase_order_detail['ref_purchase_order_detail'].qty) # approved qty
                    # print(purchase_order_detail['qty']) # order qty
                    if reference_qty < purchase_order_detail['qty']:  #
                        raise serializers.ValidationError({
                            f'item {purchase_order_detail["item"].name}':
                                f' Approved quantity :{purchase_order_detail["qty"]} should less than or equal to '
                                f'order quantity:{reference_qty} '})

                        # validation for amount values less than or equal to 0 "Zero"
            if purchase_order_detail['tax_rate'] < 0 or purchase_order_detail['discount_rate'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_order_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                                  ' cannot be less than 0'})

            if purchase_order_detail['purchase_cost'] <= 0 or purchase_order_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_order_detail["item"].name}': 'values in fields, purchase_cost and quantity '
                                                                  'cannot be less than '
                                                                  ' or equals to 0'})
            if purchase_order_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {purchase_order_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = purchase_order_detail['purchase_cost'] * purchase_order_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != purchase_order_detail['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {purchase_order_detail["item"].name}':
                            f'gross_amount calculation not valid, should be {gross_amount}'})
            sub_total = sub_total + gross_amount

            # validation for discount amount
            if purchase_order_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + purchase_order_detail['gross_amount']
                discount_rate = (purchase_order_detail['discount_amount'] *
                                 Decimal('100')) / (purchase_order_detail['purchase_cost'] *
                                                    purchase_order_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != purchase_order_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {purchase_order_detail["item"].name}':
                                f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + purchase_order_detail['discount_amount']
            elif purchase_order_detail['discountable'] is False and purchase_order_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {purchase_order_detail["item"].name}':
                                                       f'discount_amount {purchase_order_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - purchase_order_detail['discount_amount']
            if purchase_order_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = purchase_order_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != purchase_order_detail['tax_amount']:
                    raise serializers.ValidationError({f'item {purchase_order_detail["item"].name}':
                                                           f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif purchase_order_detail['taxable'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((
                purchase_order_detail['discount_amount']))) + \
                         ((gross_amount - (
                             purchase_order_detail['discount_amount'])) *
                          purchase_order_detail['tax_rate'] / Decimal('100'))

            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_order_detail['net_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {purchase_order_detail["item"].name}': f'net_amount calculation not valid : should be {net_amount}'})
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


class PurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    charge_type_name = serializers.ReadOnlyField(source='charge_type.name')

    class Meta:
        model = PurchaseAdditionalCharge
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DirectPurchaseDocumentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.first_name')
    document_type_name = serializers.ReadOnlyField(source='purchase_document_type.name', allow_null=True)

    class Meta:
        model = PurchaseDocument
        fields = ['id', 'title', 'purchase_document_type', 'document_url',
                  'remarks', 'created_date_ad', 'created_date_bs', 'created_by_name',
                  'document_type_name']
        read_only_fields = fields


# purchase master purchase_order_serializer for read_only views
class PurchaseMasterSerializer(serializers.ModelSerializer):
    additional_charges = PurchaseAdditionalChargeSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    department_name = serializers.ReadOnlyField(source='department.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)
    purchase_documents = DirectPurchaseDocumentSerializer(many=True, read_only=True)
    dropped = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['purchase_type_display', 'pay_type_display', 'created_by', 'created_date_ad',
                            'created_date_bs']

    def get_dropped(self, instance):
        purchase_details = PurchaseDetail.objects.filter(purchase=instance,
                                                         purchase__ref_purchase_order__isnull=True)
        if not purchase_details:
            return True
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


class GetPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        fields = ['id', 'code']
        read_only_fields = fields


class GetPackingTypeCodeSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = GetPackingTypeDetailCodeSerializer(many=True, read_only=True)
    location_code = serializers.ReadOnlyField(source="location.code", allow_null=True)

    class Meta:
        model = PackingTypeCode
        fields = ['id', 'code', 'location', 'purchase_order_detail',
                  'location_code', 'pack_type_detail_codes']
        read_only_fields = fields


# purchase detail purchase_order_serializer for read_only views
class PurchaseDetailSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = GetPackingTypeCodeSerializer(many=True, read_only=True)
    purchase_no = serializers.ReadOnlyField(source='purchase.purchase_no')
    item_name = serializers.ReadOnlyField(source='item.name')
    unit_name = serializers.ReadOnlyField(source='item.unit.name')
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)
    supplier_name = serializers.ReadOnlyField(source='purchase.supplier.name', allow_null=True)
    supplier = serializers.ReadOnlyField(source='purchase.supplier.id', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = "__all__"


class PurchasePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name')

    class Meta:
        model = PurchasePaymentDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# payment detail purchase_order_serializer of write only views
class SavePaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePaymentDetail
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# purchase additional charge purchase_order_serializer of write only views
class SavePurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseAdditionalCharge
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# purchase detail purchase_order_serializer for write_only views
class SavePurchaseDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

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


class SavePurchaseDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDocument
        exclude = ['purchase_main']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# nested purchase_order_serializer for purchase master with purchase detail, payment detail and
# additional charges for write_only views
class SavePurchaseMasterSerializer(serializers.ModelSerializer):
    purchase_details = SavePurchaseDetailSerializer(many=True)
    payment_details = SavePaymentDetailSerializer(many=True)
    additional_charges = SavePurchaseAdditionalChargeSerializer(many=True)
    purchase_documents = SavePurchaseDocumentsSerializer(many=True)
    unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    code_name = serializers.ReadOnlyField(source='item.code')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'fiscal_session_ad',
                            'fiscal_session_bs']

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

    # def create(self, validated_data):
    #     validated_data['created_by'] = current_user.get_created_by(self.context)

    #     date_now = timezone.now()
    #     purchase_details = validated_data.pop('purchase_details')
    #     payment_details = validated_data.pop('payment_details')
    #     additional_charges = validated_data.pop('additional_charges')
    #     purchase_documents = validated_data.pop('purchase_documents')

    #     # set fiscal year for purchase master
    #     # get current fiscal year and compare it to FiscalSessionAD and FiscalSessionBS
    #     current_fiscal_session_short_ad = get_fiscal_year_code_ad()
    #     current_fiscal_session_short_bs = get_fiscal_year_code_bs()
    #     print(current_fiscal_session_short_ad, current_fiscal_session_short_bs)
    #     try:
    #         fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
    #         fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)         

    #     except:
    #         raise serializer.ValidationError("fiscal session does not match")

    #     purchase_master = PurchaseMaster.objects.create(**validated_data, created_date_ad=date_now, fiscal_session_ad=fiscal_session_ad, fiscal_session_bs=fiscal_session_bs)

    #     for purchase_detail in purchase_details:
    #         purchase_detail["batch_no"] = generate_batch_no()
    #         PurchaseDetail.objects.create(**purchase_detail, purchase=purchase_master,
    #                                       created_by=validated_data['created_by'], created_date_ad=date_now)
    #     for payment_detail in payment_details:
    #         PurchasePaymentDetail.objects.create(**payment_detail, purchase_master=purchase_master,
    #                                              created_by=validated_data['created_by'], created_date_ad=date_now)

    #     for additional_charge in additional_charges:
    #         PurchaseAdditionalCharge.objects.create(**additional_charge, purchase_master=purchase_master,
    #                                                 created_by=validated_data['created_by'], created_date_ad=date_now)

    #     for purchase_document in purchase_documents:
    #         PurchaseDocument.objects.create(**purchase_document, purchase_main=purchase_master,
    #             created_by=validated_data['created_by'], created_date_ad=date_now)
    #     return purchase_master

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
    #         # if purchase_detail['free_purchase'] is False:
    #         #     sub_total = sub_total + gross_amount

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


"""************************** Serializers for Get Views *****************************************"""


class GetPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)

    class Meta:
        model = PackingTypeDetail
        exclude = ['created_date_ad', 'created_date_bs', 'active', 'created_by', 'item']


class GetSupplierSerializer(serializers.ModelSerializer):
    # country_name =serializer.ReadOnlyField(source='country.name', allow_null=True)
    class Meta:
        model = Supplier
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active', 'tax_reg_system', 'pan_vat_no',
                   'image']


class GetItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active', 'display_order']


class GetDiscountSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active']


class GetAdditionalChargeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalChargeType
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active']


class GetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active', 'location',
                   'stock_alert_qty', 'basic_info', 'image']


class GetPaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active', 'remarks']
