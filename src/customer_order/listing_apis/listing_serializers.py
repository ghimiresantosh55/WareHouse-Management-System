from rest_framework import serializers

from src.core_app.models import DiscountScheme
from src.customer.models import Customer
from src.customer_order.models import OrderMaster
from src.item.models import Item
from tenant.models import Tenant


class CustomerCustomerOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no']


class DiscountSchemeCustomerOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = ['id', 'name', 'rate']


class ItemCustomerOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'purchase_cost', 'sale_cost', 'name', 'discountable',
                  'taxable', 'tax_rate', 'code']


class SelfCustomerOrderListSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = ['id', 'grand_total', 'sub_total', 'order_no', 'customer_first_name',
                  'customer_last_name', 'status_display', 'created_by_user_name', 'created_date_ad', 'created_date_bs']


class TransferBranchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'
