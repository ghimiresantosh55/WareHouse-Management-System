from src.core_app.models import Country, Bank
from rest_framework import serializers
class CountryOrganizationSetupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class BankBankDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']