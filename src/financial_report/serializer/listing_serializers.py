from rest_framework.serializers import ModelSerializer

from src.customer.models import Customer
from src.item.models import Item
from src.purchase.models import PurchaseMaster
from src.sale.models import SaleMaster
from src.user.models import User
from src.supplier.models import Supplier


class ReportUserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_name', 'first_name', 'last_name']
        read_only_fields = fields


class ReportItemListSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'code']
        read_only_fields = fields


class ReportSupplierListSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', ]
        read_only_fields = fields


class ReportCustomerListSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'user']
        read_only_fields = fields


class ReportSaleListSerializer(ModelSerializer):
    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no']
        read_only_fields = fields


class ReportPurchaseReceivedListSerializer(ModelSerializer):
    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no']
        read_only_fields = fields
