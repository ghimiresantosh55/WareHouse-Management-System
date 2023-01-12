from decimal import Decimal

from rest_framework import serializers

from src.credit_management.models import CreditClearance, CreditPaymentDetail
from src.sale.models import SaleMaster


class CreditPaymentMasterSerializer(serializers.ModelSerializer):
    # displaying of created_by_user_name
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale_master.sale_no', allow_null=True)
    # dispalying of enum field. 
    # source='get_fieldname_display' is used to display enum value
    customer_first_name = serializers.ReadOnlyField(source='sale_master.customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='sale_master.customer.last_name', allow_null=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)

    class Meta:
        model = CreditClearance
        fields = "__all__"
        read_only_fields = ['payment_type_display']


class CreditPaymentDetailSerializer(serializers.ModelSerializer):
    # sale_master = serializer.ReadOnlyField(source='credit_clearance_master.creditclearancedetail.sale_master.id',
    #                                         allow_null=True)

    created_by_user_name=serializers.ReadOnlyField(source='created_by.user_name')
    payment_mode_name=serializers.ReadOnlyField(source='payment_mode.name')

    class Meta:
        model = CreditPaymentDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


"""_________________________________save credit payment details_________________________________________________"""
#
#
# class SaveCreditPaymentDetailSerializer(serializer.ModelSerializer):
#     payment_mode_name = serializer.ReadOnlyField(source='payment_mode.name')
#
#     class Meta:
#         model = CreditPaymentDetail
#         # we can also exclude fields in purchase_order_serializer
#         exclude = ['credit_clearance']
#         read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')
#
#
# # nested purchase_order_serializer
# class SaveCreditClearanceSerializer(serializer.ModelSerializer):
#     # calling of child seralizer.
#     # CreditClearance with id 1 can have multiple child in ClearanceDetail so many=True is provided.
#     credit_payment_details = SaveCreditPaymentDetailSerializer(many=True)
#
#     created_by_user_name = serializer.ReadOnlyField(source='created_by.user_name')
#
#     # get_fieldname_display is used to display value of enum field
#     payment_type_display = serializer.ReadOnlyField(source='get_payment_type_display', allow_null=True)
#
#     sale_no = serializer.ReadOnlyField(source='sale_master.sale_no', allow_null=True)
#
#     class Meta:
#         model = CreditClearance
#         fields = "__all__"
#         read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')
#
#     def create(self, validated_data):
#         date_now = timezone.now()
#         # we have added extra field in CreditClearance models (i.e. credit_payment_details) which is mentioned above.
#         # since model CreditClearance doesnot have credit_payment_details fields, it is poped.
#         credit_payment_details = validated_data.pop('credit_payment_details')
#
#         # manually passing of created_by id. We obtain it by get_created_by() function.
#         validated_data['created_by'] = get_created_by(self.context)
#
#         # data is posted in CreditClearance table.
#         credit_clearance = CreditClearance.objects.create(**validated_data, created_date_ad=date_now)
#
#         # using for loop for passing multiple value in table
#         for credit_payment_detail in credit_payment_details:
#             CreditPaymentDetail.objects.create(**credit_payment_detail, credit_clearance=credit_clearance,
#                                                created_by=validated_data['created_by'], created_date_ad=date_now)
#
#         return credit_clearance


"""_______________________ purchase_order_serializer for Credit Sale Report _______________________________________________"""


class SaleCreditSerializer(serializers.ModelSerializer):
    sale_id = serializers.ReadOnlyField(source='id')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    paid_amount = serializers.SerializerMethodField()
    due_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = SaleMaster
        fields = ['sale_id', 'sale_no', 'customer', 'customer_first_name', 'customer_middle_name', 'customer_last_name',
                  'total_amount',
                  'paid_amount', 'due_amount', 'created_date_ad', 'created_date_bs',
                  'created_by', 'created_by_user_name', 'remarks']

    def get_paid_amount(self, instance):
        # calculation of total_paid_amount with same fk
        paid_amount = sum(CreditClearance.objects.filter(sale_master=instance.id, payment_type=1)
                          .values_list('total_amount', flat=True))
        refund_amount = sum(CreditClearance.objects.filter(sale_master=instance.id, payment_type=2)
                            .values_list('total_amount', flat=True))
        return Decimal(paid_amount - refund_amount)

    # calculation of due amount
    def get_due_amount(self, instance):
        # Here, get_paid_amount() provide total paid_amount which is calculated above
        paid_amount = self.get_paid_amount(instance)

        # due_amount = (total amount to be paid) - (paid amount)
        due_amount = self.get_total_amount(instance) - paid_amount

        return due_amount

    def get_total_amount(self, instance):
        total_sale_amount = instance.grand_total
        sale_return_amount = sum(SaleMaster.objects.filter(ref_sale_master=instance.id)
                                 .values_list('grand_total', flat=True))

        return total_sale_amount - sale_return_amount
