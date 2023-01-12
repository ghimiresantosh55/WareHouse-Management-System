from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from .models import PurchaseDocument
from .models import PurchaseDocumentType


class PurchaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDocument
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        validated_data['created_date_ad'] = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        return super().create(validated_data)


class PurchaseDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDocumentType
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        validated_data['created_date_ad'] = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        return super().create(validated_data)
