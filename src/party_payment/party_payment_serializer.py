from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.purchase.models import PurchaseMaster
from src.supplier.models import Supplier
from .models import PartyPayment, PartyPaymentDetail
from .party_payment_service import SupplierPartyPayment
from .reciept_unique_id_generator import get_receipt_no


class SavePartyPaymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyPaymentDetail
        fields = ['id', 'payment_mode', 'payment_id', 'amount', 'remarks']


class SavePartyPaymentMasterSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(active=True), write_only=True, required=False
    )
    purchase_master = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseMaster.objects.filter(pay_type=2), required=False
    )
    party_payment_details = SavePartyPaymentDetailsSerializer(many=True)

    class Meta:
        model = PartyPayment
        fields = ['id', 'receipt_no', 'purchase_master', 'supplier',
                  'payment_type', 'total_amount', 'remarks', 'party_payment_details']
        read_only_fields = ['receipt_no']

    def create(self, validated_data):
        supplier = validated_data.get("supplier", False)
        purchase_master = validated_data.get("purchase_master", False)
        if supplier:
            party_payment = SupplierPartyPayment(
                supplier=supplier, party_payment_details=validated_data['party_payment_details']
            )
            party_payment.save_party_payment(self.context)

        elif purchase_master:
            created_date_ad = timezone.now()
            created_by = current_user.get_created_by(self.context)
            party_payment_details = validated_data.pop('party_payment_details')
            party_payment = PartyPayment.objects.create(
                **validated_data, receipt_no=get_receipt_no(),
                created_date_ad=created_date_ad, created_by=created_by
            )
            for party_payment_detail in party_payment_details:
                PartyPaymentDetail.objects.create(
                    **party_payment_detail, created_by=created_by,
                    created_date_ad=created_date_ad, party_payment=party_payment
                )
            validated_data['party_payment_details'] = party_payment_details
        return validated_data

    def validate(self, attrs):
        if attrs['total_amount'] <= 0:
            raise serializers.ValidationError({"message": "total_amount cannot be zero or less than zero"})
        return super().validate(attrs)
