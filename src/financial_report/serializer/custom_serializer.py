from rest_framework import serializers

from src.party_payment.models import BasicPartyPayment


class BasicPartyPaymentSummaryReportSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    middle_name = serializers.CharField()
    last_name = serializers.CharField()
    total_purchase_cash = serializers.FloatField()
    total_purchase_credit = serializers.FloatField()
    total_purchase_return_cash = serializers.FloatField()
    total_purchase_return_credit = serializers.FloatField()
    party_payment_payment = serializers.FloatField()
    party_payment_payment_return = serializers.FloatField()
    to_be_paid = serializers.FloatField()
    paid_amount = serializers.FloatField()
    adv_due_amount = serializers.FloatField()

    class Meta:
        model = BasicPartyPayment
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'total_purchase_cash', 'total_purchase_credit',
                  'total_purchase_return_cash',
                  'total_purchase_return_credit', 'party_payment_payment', 'party_payment_payment_return', 'to_be_paid',
                  'paid_amount', 'adv_due_amount']
        read_only_fields = ['id', 'first_name', 'middle_name', 'last_name', 'total_purchase_cash',
                            'total_purchase_credit', 'total_purchase_return_cash',
                            'total_purchase_return_credit', 'party_payment_payment', 'party_payment_payment_return',
                            'to_be_paid', 'paid_amount', 'adv_due_amount']
