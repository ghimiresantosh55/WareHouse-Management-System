from rest_framework import serializers

from src.customer.models import CustomerIsSupplier


class PartyReportSerializer(serializers.ModelSerializer):
    purchase = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    party_payment = serializers.SerializerMethodField()
    party_refund = serializers.SerializerMethodField()
    credit_payment = serializers.SerializerMethodField()
    credit_refund = serializers.SerializerMethodField()

    class Meta:
        model = CustomerIsSupplier
        fields = ['id', 'supplier', 'customer']

    def get_purchase(self, instance):
        purchase_data = {}
        pass

    def get_sale(self, instance):
        pass


class SupplierAndCustomerReportSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    party_name = serializers.CharField(max_length=100)
    operation_type = serializers.CharField(max_length=10)
    debit = serializers.DecimalField(max_digits=20, decimal_places=2)
    credit = serializers.DecimalField(max_digits=20, decimal_places=2)
    created_date_ad = serializers.DateTimeField()
