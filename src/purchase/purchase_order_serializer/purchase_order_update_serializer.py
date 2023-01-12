from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from ..models import PurchaseOrderDetail, PurchaseOrderDocument
from ..models import PurchaseOrderMaster
from ..serializers import SavePurchaseOrderDocumentsSerializer


class CancelSinglePurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDetail
        fields = ['id', 'cancelled', 'remarks']
        extra_kwargs = {
            'remarks': {'required': True}
        }

    def update(self, instance, validated_data):
        instance.cancelled = True
        instance.remarks = validated_data['remarks']
        instance.save()

        # update purchase order master
        purchase_order_master = instance.purchase_order
        purchase_order_master.sub_total -= instance.gross_amount
        purchase_order_master.grand_total -= instance.net_amount
        prob_taxable_amount = instance.gross_amount
        if instance.discountable is True:
            purchase_order_master.total_discount = purchase_order_master.total_discount - instance.discount_amount
            purchase_order_master.total_discountable_amount = purchase_order_master.total_discountable_amount - instance.gross_amount
            prob_taxable_amount = prob_taxable_amount - instance.discount_amount
        if instance.taxable is True:
            purchase_order_master.total_tax = purchase_order_master.total_tax - instance.tax_amount
            purchase_order_master.total_taxable_amount = purchase_order_master.total_taxable_amount - prob_taxable_amount
        else:
            purchase_order_master.total_non_taxable_amount = purchase_order_master.total_taxable_amount - prob_taxable_amount
        purchase_order_master.save()
        return instance


class CancelPurchaseOrderSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        purchase_order_master = instance
        purchase_order_master.order_type = 2
        purchase_order_master.purchase_order_details.all().update(
            cancelled=True
        )
        purchase_order_master.save()
        return validated_data


class UpdatePurchaseOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDetail
        fields = ['id', 'item', 'item_category',
                  'purchase_cost', 'sale_cost', 'qty',
                  'pack_qty', 'packing_type', 'packing_type_detail',
                  'taxable', 'tax_rate', 'tax_amount',
                  'discountable', 'discount_rate', 'discount_amount',
                  'gross_amount', 'net_amount', 'ref_purchase_order_detail',
                  'created_by', 'created_date_bs', 'created_date_ad']

        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class UpdatePurchaseOrderSerializer(serializers.ModelSerializer):
    purchase_order_details = UpdatePurchaseOrderDetailSerializer(many=True, required=False)
    purchase_order_documents = SavePurchaseOrderDocumentsSerializer(many=True, required=False)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def update(self, instance, validated_data):
        current_date = timezone.now()

        try:
            purchase_order_details = validated_data.pop('purchase_order_details')
        except KeyError:
            purchase_order_details = []

        try:
            purchase_order_documents = validated_data.pop('purchase_order_documents')
        except KeyError:
            purchase_order_documents = []

        created_by = current_user.get_created_by(self.context)

        instance.sub_total = validated_data.get("sub_total", instance.sub_total)
        instance.discount_scheme = validated_data.get("discount_scheme", instance.discount_scheme)
        instance.total_discount = validated_data.get("total_discount", instance.total_discount)
        instance.discount_rate = validated_data.get("discount_rate", instance.discount_rate)
        instance.total_discountable_amount = validated_data.get("total_discountable_amount",
                                                                instance.total_discountable_amount)
        instance.total_taxable_amount = validated_data.get("total_taxable_amount", instance.total_taxable_amount)
        instance.total_non_taxable_amount = validated_data.get("total_non_taxable_amount",
                                                               instance.total_non_taxable_amount)
        instance.total_tax = validated_data.get("total_tax", instance.total_tax)
        instance.grand_total = validated_data.get("grand_total", instance.grand_total)
        instance.supplier = validated_data.get("supplier", instance.supplier)
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.terms_of_payment = validated_data.get("terms_of_payment", instance.terms_of_payment)
        instance.shipment_terms = validated_data.get("shipment_terms", instance.shipment_terms)
        instance.attendee = validated_data.get("attendee", instance.attendee)
        instance.end_user_name = validated_data.get("end_user_name", instance.end_user_name)
        instance.save()
        for purchase_order_detail in purchase_order_details:
            PurchaseOrderDetail.objects.create(
                **purchase_order_detail, purchase_order=instance,
                created_by=created_by,
                created_date_ad=current_date
            )
        for purchase_order_document in purchase_order_documents:
            PurchaseOrderDocument.objects.create(
                **purchase_order_document, purchase_order=instance,
                created_by=created_by,
                created_date_ad=current_date
            )
        return instance


class PurchaseOrderDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDetail
        fields = ['id', 'item', 'item_category',
                  'purchase_cost', 'sale_cost', 'qty',
                  'pack_qty', 'packing_type', 'packing_type_detail',
                  'taxable', 'tax_rate', 'tax_amount',
                  'discountable', 'discount_rate', 'discount_amount',
                  'gross_amount', 'net_amount', 'ref_purchase_order_detail',
                  'created_by', 'created_date_bs', 'created_date_ad']

        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

        extra_kwargs = {
            'id': {'required': True,
                   'read_only': False},
        }


class UpdateDetailPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = PurchaseOrderDetailUpdateSerializer(write_only=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = ['purchase_order_details', 'sub_total', 'discount_scheme', 'total_discount',
                  'discount_rate', 'total_discountable_amount',
                  'total_non_taxable_amount', 'total_taxable_amount',
                  'total_tax', 'grand_total', 'supplier', 'remarks', 'terms_of_payment', 'shipment_terms',
                  'attendee', 'end_user_name'
                  ]

    def update(self, instance, validated_data):
        purchase_order_details = validated_data.pop('purchase_order_details')

        instance.sub_total = validated_data.get("sub_total", instance.sub_total)
        instance.discount_scheme = validated_data.get("discount_scheme", instance.discount_scheme)
        instance.total_discount = validated_data.get("total_discount", instance.total_discount)
        instance.discount_rate = validated_data.get("discount_rate", instance.discount_rate)
        instance.total_discountable_amount = validated_data.get("total_discountable_amount",
                                                                instance.total_discountable_amount)
        instance.total_taxable_amount = validated_data.get("total_taxable_amount", instance.total_taxable_amount)
        instance.total_non_taxable_amount = validated_data.get("total_non_taxable_amount",
                                                               instance.total_non_taxable_amount)
        instance.total_tax = validated_data.get("total_tax", instance.total_tax)
        instance.grand_total = validated_data.get("grand_total", instance.grand_total)
        instance.supplier = validated_data.get("supplier", instance.supplier)
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.terms_of_payment = validated_data.get("terms_of_payment", instance.terms_of_payment)
        instance.shipment_terms = validated_data.get("shipment_terms", instance.shipment_terms)
        instance.attendee = validated_data.get("attendee", instance.attendee)
        instance.end_user_name = validated_data.get("end_user_name", instance.end_user_name)
        instance.save()
        # update in purchase order detail
        # purchase_order_detail_instance = purchase order detail

        try:
            purchase_order_detail = PurchaseOrderDetail.objects.get(pk=purchase_order_details['id'])
        except Exception:
            raise serializers.ValidationError({"error": f"Purchase Order Detail {purchase_order_details['id']} cannot "
                                                        f"be found "})

        purchase_order_detail.item = purchase_order_details.get("item", purchase_order_detail.item)
        purchase_order_detail.item_category = purchase_order_details.get("item_category",
                                                                         purchase_order_detail.item_category)
        purchase_order_detail.purchase_cost = purchase_order_details.get("purchase_cost",
                                                                         purchase_order_detail.purchase_cost)
        purchase_order_detail.sale_cost = purchase_order_details.get("sale_cost",
                                                                     purchase_order_detail.sale_cost)
        purchase_order_detail.qty = purchase_order_details.get("qty", purchase_order_detail.qty)
        purchase_order_detail.pack_qty = purchase_order_details.get("pack_qty",
                                                                    purchase_order_detail.pack_qty)
        purchase_order_detail.packing_type = purchase_order_details.get("packing_type",
                                                                        purchase_order_detail.packing_type)
        purchase_order_detail.packing_type_detail = purchase_order_details.get("packing_type_detail",
                                                                               purchase_order_detail.packing_type_detail)
        purchase_order_detail.taxable = purchase_order_details.get("taxable", purchase_order_detail.taxable)
        purchase_order_detail.tax_rate = purchase_order_details.get("tax_rate", purchase_order_detail.tax_rate)
        purchase_order_detail.tax_amount = purchase_order_details.get("tax_amount",
                                                                      purchase_order_detail.tax_amount)
        purchase_order_detail.discountable = purchase_order_details.get("discountable",
                                                                        purchase_order_detail.discountable)
        purchase_order_detail.discount_rate = purchase_order_details.get("discount_rate",
                                                                         purchase_order_detail.discount_rate)
        purchase_order_detail.discount_amount = purchase_order_details.get("discount_amount",
                                                                           purchase_order_detail.discount_amount)
        purchase_order_detail.gross_amount = purchase_order_details.get("gross_amount",
                                                                        purchase_order_detail.gross_amount)
        purchase_order_detail.net_amount = purchase_order_details.get("net_amount",
                                                                      purchase_order_detail.net_amount)
        purchase_order_detail.ref_purchase_order_detail = purchase_order_details.get("ref_purchase_order_detail",
                                                                                     purchase_order_detail.ref_purchase_order_detail)

        purchase_order_detail.save()

        return instance
