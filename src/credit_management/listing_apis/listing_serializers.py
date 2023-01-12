from rest_framework import serializers

from src.core_app.models import PaymentMode
from src.customer.models import Customer


class CustomerCreditClearanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no', 'phone_no']
        read_only_fields = fields


class PaymentModeCreditClearanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id', 'name', 'remarks']
        read_only_fields = fields
