from rest_framework import serializers

from src.credit_management.models import CreditClearance
from src.sale.models import SaleMaster


class SaleCreditClearanceSummarySerializer(serializers.ModelSerializer):
    payment_type_name = serializers.ReadOnlyField(source='get_payment_type_display')

    class Meta:
        model = CreditClearance
        fields = ['id', 'payment_type_name', 'receipt_no', 'total_amount']
        read_only_fields = fields


class SaleCreditReportSummarySerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    paid_amount = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    returned_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    credit_clearances = SaleCreditClearanceSummarySerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'customer', 'customer_first_name', 'customer_middle_name', 'customer_last_name',
                  'paid_amount', 'refund_amount', 'returned_amount', 'total_amount', 'created_date_ad',
                  'created_date_bs',
                  'created_by', 'created_by_user_name', 'remarks', 'credit_clearances']
        read_only_fields = fields

    def to_representation(self, instance):
        data = super(SaleCreditReportSummarySerializer, self).to_representation(instance)

        # get due amount
        data['due_amount'] = (data['total_amount'] - data['returned_amount']) - (
                data['paid_amount'] - data['refund_amount'])
        return data

    def get_paid_amount(self, instance):
        # calculation of total_paid_amount with same fk
        paid_amount = sum(CreditClearance.objects.filter(sale_master=instance.id, payment_type=1)
                          .values_list('total_amount', flat=True))

        return paid_amount

    def get_refund_amount(self, instance):
        refund_amount = sum(CreditClearance.objects.filter(sale_master=instance.id, payment_type=2)
                            .values_list('total_amount', flat=True))
        return refund_amount

    def get_total_amount(self, instance):
        total_sale_amount = instance.grand_total
        return total_sale_amount

    def get_returned_amount(self, instance):
        sale_return_amount = sum(SaleMaster.objects.filter(ref_sale_master=instance.id)
                                 .values_list('grand_total', flat=True))
        return sale_return_amount
