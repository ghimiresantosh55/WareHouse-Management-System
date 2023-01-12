from rest_framework import serializers

from src.chalan.models import ChalanMaster
from src.customer.models import Customer


class CustomerChalanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no']
        read_only_fields = fields


class ChalanNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no']
        read_only_fields = fields
