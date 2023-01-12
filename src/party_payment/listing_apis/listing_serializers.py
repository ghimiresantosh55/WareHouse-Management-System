from rest_framework import serializers

from src.core_app.models import PaymentMode
from src.supplier.models import Supplier


class SupplierPartyPaymentListSerializer(serializers.ModelSerializer):
    credit_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    due_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'credit_amount', 'paid_amount',
                  'pan_vat_no', 'phone_no', 'due_amount']
        read_only_fields = fields


class PaymentModePartyPaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id', 'name', 'remarks']
        read_only_fields = fields
