from django.utils import timezone
from rest_framework import serializers

from .models import QuotationMaster, QuotationDetail
from .quotation_unique_id_generator import generate_quotation_no
from ..custom_lib.functions import current_user
from ..customer.models import Customer
from ..item.models import Item


class QuotationOrderSummaryCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'address']


class QuotationSummaryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class QuotationMasterSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer = serializers.SerializerMethodField()

    class Meta:
        model = QuotationMaster
        fields = '__all__'

    def get_customer(self, instance):
        return {
            "first_name": instance.customer.first_name,
            "last_name": instance.customer.last_name,
            "id": instance.customer.pk,
        }


class QuotationDetailViewSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(
        source='created_by.user_name', allow_null=True
    )

    class Meta:
        model = QuotationDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


class QuotationSummaryDetailSerializer(serializers.ModelSerializer):
    item = QuotationSummaryItemSerializer(read_only=True)

    class Meta:
        model = QuotationDetail
        exclude = ['quotation']


class QuotationSummaryMasterSerializer(serializers.ModelSerializer):
    customer = QuotationOrderSummaryCustomerSerializer(read_only=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    quotation_details = QuotationSummaryDetailSerializer(many=True, read_only=True)

    class Meta:
        model = QuotationMaster
        fields = '__all__'


class SaveQuotationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationDetail
        exclude = ['quotation', 'cancelled', 'device_type', 'app_type']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveQuotationSerializer(serializers.ModelSerializer):
    quotation_details = SaveQuotationDetailSerializer(many=True)

    class Meta:
        model = QuotationMaster
        fields = ['id', 'quotation_details', 'customer', 'remarks']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'quotation_no']

    def create(self, validated_data):
        date_now = timezone.now()

        quotation_details = validated_data.pop('quotation_details')
        created_by = current_user.get_created_by(self.context)
        quotation_master = QuotationMaster.objects.create(
            quotation_no=generate_quotation_no(),
            **validated_data, created_date_ad=date_now,
            created_by=created_by,
            cancelled=False
        )

        for detail in quotation_details:
            QuotationDetail.objects.create(**detail, quotation=quotation_master,
                                           created_by=created_by,
                                           created_date_ad=date_now,
                                           cancelled=False)

        return quotation_master


class UpdateQuotationSerializer(serializers.ModelSerializer):
    quotation_details = SaveQuotationDetailSerializer(many=True, required=False)
    quotation_no = serializers.CharField(max_length=20, read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.filter(active=True), required=False)
    delivery_date_ad = serializers.DateField(allow_null=True, required=False)
    customer_first_name = serializers.ReadOnlyField(source="customer.first_name", allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source="customer.middle_name", allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source="customer.last_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = QuotationMaster
        fields = ['id', 'quotation_no', 'quotation_details', 'customer', 'delivery_date_ad',
                  'customer_first_name', 'customer_middle_name', 'customer_last_name',
                  'delivery_date_bs',
                  'remarks', 'created_by_user_name']
        read_only_fields = ['delivery_date_bs']

    def update(self, instance, validated_data):
        # date_now = timezone.now()
        # quotation_details = validated_data.pop('quotation_details')
        # created_by = current_user.get_created_by(self.context)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.delivery_date_ad = validated_data.get('delivery_date_ad', instance.delivery_date_ad)
        instance.delivery_location = validated_data.get('delivery_location', instance.delivery_location)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.save()

        # if quotation_details:
        #     for detail in quotation_details:
        #         print(detail)
        # QuotationDetail.objects.create(**detail, quotation=instance,
        #                                created_by=created_by,
        #                                created_date_ad=date_now,
        #                                cancelled=False)
        return instance


class UpdateQuotationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationDetail
        fields = ['qty', 'sale_cost']


class CancelSingleQuotationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationDetail
        fields = ["cancelled", "item", "item_category", "qty", "sale_cost",
                  "remarks"]

    def update(self, instance, validated_data):
        instance.cancelled = True
        instance.remarks = validated_data['remarks']
        instance.save()

        return instance


class CancelQuotationMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationMaster
        fields = ['id', 'quotation_no', 'customer', 'remarks', 'cancelled']
        read_only_fields = fields

    def update(self, instance, validated_data):
        instance.cancelled = True
        instance.save()
        quotation_details = instance.quotation_details.all()
        for quotation_detail in quotation_details:
            quotation_detail.cancelled = True
            quotation_detail.save()
        return instance

# class CustomerOrderItemTestForQuotationSerializer(serializers.ModelSerializer):
#     quotation_details = QuotationSummaryDetailSerializer(many=True, read_only=True)
#     customer = QuotationOrderSummaryCustomerSerializer(read_only=True)
#     created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
#
#     class Meta:
#         model = QuotationMaster
#         fields = ['id','customer', 'created_by_user_name', 'quotation_details']
