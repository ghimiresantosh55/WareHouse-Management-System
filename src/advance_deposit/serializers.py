from rest_framework import serializers, status
from .models import OrderMaster
from src.custom_lib.functions import current_user
from django.utils import timezone
from decimal import Decimal
from src.advance_deposit.models import AdvancedDeposit, AdvancedDepositPaymentDetail
from .advance_deposit_unique_id_generator import generate_advanced_deposit_no


class AdvancedDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedDeposit
        fields = "__all__"


class AdvancedDepositPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedDepositPaymentDetail
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveAdvancedDepositPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = AdvancedDepositPaymentDetail
        exclude = ["advanced_deposit"]
        read_only_fields = ['payment_mode_name', 'created_date_ad', 'created_date_bs', 'created_by']


class SaveAdvancedDepositSerializer(serializers.ModelSerializer):
    advanced_deposit_payment_details = SaveAdvancedDepositPaymentDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = AdvancedDeposit
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'deposit_no']

    def create(self, validated_data):
        date_now = timezone.now()
        payment_details = validated_data.pop('advanced_deposit_payment_details')
        if not payment_details:
            raise serializers.ValidationError("Please provide at least one payment detail")

        validated_data['created_by'] = current_user.get_created_by(self.context)
        validated_data['deposit_no'] = generate_advanced_deposit_no()
        advanced_deposit = AdvancedDeposit.objects.create(**validated_data, created_date_ad=date_now)

        for detail in payment_details:
            AdvancedDepositPaymentDetail.objects.create(**detail, advanced_deposit=advanced_deposit,
                                                        created_by=validated_data['created_by'],
                                                        created_date_ad=date_now)
        return advanced_deposit

    def validate(self, data):
        order_master = data['order_master']
        advanced_payment_amount = data['amount']
        # raise serializer.ValidationError({'amount_no_valid':'Advance deposit must not be greater than total_amount'})

        order_amount = OrderMaster.objects.get(id=order_master.id).grand_total
        older_advanced_payments = sum(
            AdvancedDeposit.objects.filter(order_master=order_master.id).values_list('amount', flat=True))
        advanced_payment_amount += older_advanced_payments
        if order_amount < advanced_payment_amount:
            raise serializers.ValidationError(
                {'amount_no_valid': 'Advance deposit must not be greater than total_amount'})

        payment_details = data['advanced_deposit_payment_details']
        total_amount = Decimal('0.00')
        for payment in payment_details:
            total_amount += payment['amount']
        if total_amount != data['amount']:
            raise serializers.ValidationError('Advanced deposit amount not equal to'
                                              ' advanced_deposit_payment_detail amount')

        return data
