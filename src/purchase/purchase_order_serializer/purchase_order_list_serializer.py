from decimal import Decimal

from django.forms import model_to_dict
from rest_framework import serializers

from src.item.models import PackingTypeDetail
from ..models import PurchaseOrderMaster, PurchaseOrderDetail, PurchaseOrderDocument
from ..serializers import GetPackingTypeDetailSerializer


class PendingPurchaseOrderMasterDocumentListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.first_name')
    document_type_name = serializers.ReadOnlyField(source='document_type.name')

    class Meta:
        model = PurchaseOrderDocument
        fields = ['id', 'title', 'document_type', 'document_url',
                  'remarks', 'created_date_ad', 'created_date_bs', 'created_by_name',
                  'document_type_name']
        read_only_fields = fields


class PendingPurchaseOrderMasterListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    purchase_order_documents = PendingPurchaseOrderMasterDocumentListSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_bs', 'created_date_ad', 'sub_total',
                  'total_discount', 'total_tax', 'grand_total', 'created_by_user_name',
                  'supplier', 'status', 'remarks', 'purchase_order_documents', 'currency', 'department']
        read_only_fields = fields

    def get_status(self, instance):
        if instance.order_type == 2:
            return "CANCELLED"
        elif instance.order_type == 1:
            if not instance.self_purchase_order_master.all().exists():
                return "PENDING"

            order_details_sum = sum(
                instance.purchase_order_details.values_list('qty', flat=True)
            )

            ref_order_details_qty_sum = sum(
                PurchaseOrderDetail.objects.filter(purchase_order__ref_purchase_order=instance, ).values_list('qty',
                                                                                                              flat=True)
            )
            purchase_order_qty_details = PurchaseOrderDetail.objects.filter(purchase_order=instance)
            received = sum(purchase_order_qty_details.filter(cancelled=False).values_list('qty', flat=True))
            if ref_order_details_qty_sum < order_details_sum and ref_order_details_qty_sum != received:
                return "PARTIAL"
            return "RECEIVED"

    def get_supplier(self, instance):
        try:
            supplier = {
                "id": instance.supplier.id,
                "name": instance.supplier.name
            }
            return supplier
        except Exception:
            return {}

    def get_department(self, instance):
        try:
            supplier = {
                "id": instance.department.id,
                "name": instance.department.name,
                "code": instance.department.code
            }
            return supplier
        except Exception:
            return {}


# purchase order detail serializer for Read Only purchase_order_view
class PurchaseOrderDetailMasterRetrieveSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_code = serializers.ReadOnlyField(source='item.code', allow_null=True)
    item_basic_info = serializers.ReadOnlyField(source='item.basic_info', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    item_harmonic_code = serializers.ReadOnlyField(source='item.harmonic_code', allow_null=True)
    item_taxable = serializers.ReadOnlyField(source='item.taxable', allow_null=True)
    item_discountable = serializers.ReadOnlyField(source='item.discountable', allow_null=True)
    packing_type_details_itemwise = serializers.SerializerMethodField()
    packing_type_detail = serializers.SerializerMethodField()
    received_qty = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderDetail
        fields = ['id', 'item_name', 'item_category_name', 'item_harmonic_code',
                  'item_basic_info', 'packing_type', 'item', 'received_qty', 'item_category', 'tax_rate',
                  'qty', 'item_taxable', 'item_discountable', 'discount_amount',
                  'tax_amount', 'discount_rate', 'gross_amount', 'net_amount', 'item_code', 'purchase_cost',
                  'packing_type_details_itemwise', 'packing_type_detail', 'cancelled'
                  ]
        read_only_fields = fields

    def get_packing_type_detail(self, instance):
        if instance.packing_type_detail:
            return {
                "id": instance.packing_type_detail.id,
                "pack_qty": instance.packing_type_detail.pack_qty,
                "packing_type_name": instance.packing_type_detail.packing_type.name,
            }
        return ""

    @staticmethod
    def get_packing_type_details_itemwise(purchase_detail):
        try:
            packing_type_details_itemwise = PackingTypeDetail.objects.filter(item=purchase_detail.item.id)
            packing_serializer = GetPackingTypeDetailSerializer(packing_type_details_itemwise, many=True)
            return packing_serializer.data
        except:
            return None

    def get_received_qty(self, instance):

        received = sum(instance.self_purchase_order_detail.filter(cancelled=False).values_list('qty', flat=True))
        quantize_places = Decimal(10) ** -2
        return str(Decimal(received).quantize(quantize_places))


class PendingPurchaseOrderMasterRetrieveSerializer(serializers.ModelSerializer):
    purchase_order_details = PurchaseOrderDetailMasterRetrieveSerializer(many=True, read_only=True)
    supplier = serializers.SerializerMethodField()
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    discount_scheme = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    purchase_order_documents = PendingPurchaseOrderMasterDocumentListSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_bs', 'created_date_ad', 'sub_total',
                  'total_discount', 'total_tax', 'grand_total', 'created_by_user_name',
                  'remarks', 'end_user_name', 'terms_of_payment', 'shipment_terms',
                  'attendee', 'discount_scheme', 'supplier',
                  'purchase_order_details', 'remarks', 'currency', 'currency_exchange_rate',
                  'purchase_order_documents', 'department']
        read_only_fields = fields

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

    def get_discount_scheme(self, instance):
        discount_scheme = instance.discount_scheme
        if discount_scheme:
            return model_to_dict(discount_scheme, fields=['id', 'name', 'rate'])
        return None

    def get_currency(self, instance):
        try:
            currency = instance.currency
            return {
                "id": currency.id,
                "name": currency.name,
                "symbol": currency.symbol,
                "code": currency.code,
            }
        except AttributeError:
            return None
