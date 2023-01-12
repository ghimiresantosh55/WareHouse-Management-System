from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.purchase.models import PurchaseMaster, PurchaseOrderMaster, PurchaseDocument, PurchaseOrderDocument


class AddPurchaseOrderDocumentsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDocument
        fields = ['id', 'title', 'document_type', 'document_url', 'remarks']


class AddPurchaseOrderDocumentsSerializer(serializers.Serializer):
    purchase_order_master = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrderMaster.objects.all())
    purchase_order_documents = AddPurchaseOrderDocumentsDetailSerializer(many=True)

    def create(self, validated_data):
        created_by = current_user.get_created_by(self.context)
        date_now = timezone.now()
        purchase_order_documents = validated_data['purchase_order_documents']
        for purchase_order_document in purchase_order_documents:
            PurchaseOrderDocument.objects.create(
                **purchase_order_document,
                created_by=created_by,
                created_date_ad=date_now,
                purchase_order=validated_data['purchase_order_master']
            )

        return validated_data


class AddPurchaseDocumentsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDocument
        fields = ['id', 'title', 'purchase_document_type', 'document_url', 'remarks']


class AddPurchaseDocumentsSerializer(serializers.Serializer):
    purchase_master = serializers.PrimaryKeyRelatedField(queryset=PurchaseMaster.objects.all())
    purchase_documents = AddPurchaseDocumentsDetailSerializer(many=True)

    def create(self, validated_data):
        created_by = current_user.get_created_by(self.context)
        date_now = timezone.now()
        purchase_documents = validated_data['purchase_documents']
        for purchase_document in purchase_documents:
            PurchaseDocument.objects.create(
                **purchase_document,
                created_by=created_by,
                purchase_main=validated_data['purchase_master'],
                created_date_ad=date_now
            )

        return validated_data
