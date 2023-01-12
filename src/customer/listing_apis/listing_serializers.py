from rest_framework import serializers

from src.core_app.models import Country
from src.supplier.models import Supplier


class CountryCustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class SupplierCustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'pan_vat_no']
