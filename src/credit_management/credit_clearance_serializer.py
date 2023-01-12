from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.customer.models import Customer
from src.sale.models import SaleMaster
from .credit_management_service import CustomerCreditClearance
from .models import CreditClearance, CreditPaymentDetail
from .reciept_unique_id_generator import get_receipt_no


class SaveCreditClearanceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPaymentDetail
        fields = ['id', 'payment_mode', 'payment_id', 'amount', 'remarks']


class SaveCreditClearanceSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(active=True), write_only=True, required=False
    )
    sale_master = serializers.PrimaryKeyRelatedField(
        queryset=SaleMaster.objects.filter(pay_type=2), required=False
    )
    credit_payment_details = SaveCreditClearanceDetailsSerializer(many=True)

    class Meta:
        model = CreditClearance
        fields = ['id', 'receipt_no', 'sale_master', 'customer',
                  'payment_type', 'total_amount', 'remarks', 'credit_payment_details']
        read_only_fields = ['receipt_no']

    def create(self, validated_data):
        customer = validated_data.get("customer", False)
        sale_masters = validated_data.get("sale_master", False)
        if customer:
            credit_clearance = CustomerCreditClearance(
                customer=customer,
                credit_payment_details=validated_data['credit_payment_details']
            )
            credit_clearance.save_credit_clearance(self.context)

        elif sale_masters:
            created_date_ad = timezone.now()
            created_by = current_user.get_created_by(self.context)
            credit_payment_details = validated_data.pop('credit_payment_details')
            credit_clearance = CreditClearance.objects.create(
                **validated_data, receipt_no=get_receipt_no(),
                created_date_ad=created_date_ad, created_by=created_by
            )
            for credit_payment_detail in credit_payment_details:
                CreditPaymentDetail.objects.create(
                    **credit_payment_detail, created_by=created_by,
                    created_date_ad=created_date_ad, credit_clearance=credit_clearance
                )
            validated_data['credit_payment_details'] = credit_payment_details
        return validated_data

    def validate(self, attrs):
        if attrs['total_amount'] <= 0:
            raise serializers.ValidationError({"message": "total_amount cannot be zero or less than zero"})
        return super().validate(attrs)
