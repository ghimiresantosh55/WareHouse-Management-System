from src.core_app.models import Country
from rest_framework import serializers

from src.customer.models import Customer


class CountrySupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class CustomerSupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no']