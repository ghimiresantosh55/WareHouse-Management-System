# rest_framework
from django.db.models import F
from rest_framework import serializers

# Models from purchase app
from src.purchase.models import PurchaseOrderMaster, PurchaseOrderDetail

"""-------------------------purchase_order_serializer for purchase order -----------------------------------------------------------"""


# purchase order serializer
class ReportPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    status = serializers.SerializerMethodField()
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_bs', 'created_date_ad', 'sub_total',
                  'total_discount', 'total_tax', 'grand_total', 'supplier_name',
                  'created_by_user_name', 'discount_scheme_name',
                  'supplier', 'status', 'order_type_display', 'remarks',
                  'purchase_order_documents', 'currency', 'ref_purchase_order_no']

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

    def to_representation(self, instance):
        my_fields = {'supplier_name', 'created_by_user_name', 'discount_scheme_name', 'ref_purchase_order_no'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# purchase order detail serializer for Read Only purchase_order_view
class DetailPurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = PurchaseOrderDetail
        exclude = ['purchase_order']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

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


# purchase order master serializer for Write Only purchase_order_view
class SummaryPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = DetailPurchaseOrderDetailSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    status = serializers.SerializerMethodField()
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_bs', 'created_date_ad', 'sub_total',
                  'total_discount', 'total_tax', 'grand_total', 'supplier_name',
                  'created_by_user_name', 'discount_scheme_name',
                  'supplier', 'status', 'order_type_display', 'remarks',
                  'purchase_order_documents', 'currency', 'ref_purchase_order_no', 'purchase_order_details']

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

    def to_representation(self, instance):
        my_fields = {'supplier_name', 'created_by_user_name', 'discount_scheme_name', 'ref_purchase_order_no'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# purchase order detail serializer for Read Only purchase_order_view
class PurchaseOrderDetailReceivedAndVerifiedSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    purchase_order_received = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderDetail
        fields = ["id", 'cancelled', 'item_name', 'item_category_name', 'item', 'item_category',
                  'purchase_cost', 'sale_cost', 'qty', 'net_amount', 'discount_amount', 'tax_amount',
                  'created_date_ad', 'created_date_bs', 'purchase_order_received']
        read_only_fields = fields

    def get_purchase_order_received(self, instance):
        data = []
        if instance.self_purchase_order_detail.all().exists():
            purchase_order_received_details = instance.self_purchase_order_detail.all()
            for purchase_order_received_detail in purchase_order_received_details:
                purchase_order_received_data = {
                    'id': purchase_order_received_detail.id,
                    'order_no': purchase_order_received_detail.purchase_order.order_no,
                    'item': purchase_order_received_detail.item.name,
                    'qty': purchase_order_received_detail.qty,
                    'net_amount': purchase_order_received_detail.net_amount,
                    'created_date_ad': purchase_order_received_detail.created_date_ad,
                    'created_date_bs': purchase_order_received_detail.created_date_bs,
                    'purchase_order_verified': purchase_order_received_detail.self_purchase_order_detail.annotate(
                        verification_no=F("purchase_order__order_no")
                    ).values(
                        'id', 'verification_no', 'item', 'qty', 'net_amount', 'created_date_ad', 'created_date_bs')}

                data.append(purchase_order_received_data)

        return data


class PurchaseOrderMasterReceivedAndVerifiedSerializer(serializers.ModelSerializer):
    purchase_order_details = PurchaseOrderDetailReceivedAndVerifiedSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    status = serializers.SerializerMethodField()
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)

    # ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_bs', 'created_date_ad', 'sub_total',
                  'total_discount', 'total_tax', 'grand_total', 'supplier_name',
                  'created_by_user_name', 'discount_scheme_name',
                  'supplier', 'status', 'order_type_display', 'remarks',
                  'currency', 'purchase_order_details']

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

    def to_representation(self, instance):
        my_fields = {'supplier_name', 'created_by_user_name', 'discount_scheme_name', 'ref_purchase_order_no'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data
