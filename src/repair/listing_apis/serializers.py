
from rest_framework import serializers
from src.sale.models import SaleMaster, SaleDetail
from src.customer.models import Customer
from src.repair.models import Repair, RepairDetail, RepairUser
from src.repair.serializers import RepairDetailSerializer


class GetRepairUserSerializer(serializers.ModelSerializer):
    repair_status_display=serializers.ReadOnlyField(source='get_repair_status_display', allow_null=True)
    class Meta:
        model = RepairUser
        fields=['repair_status_display']


class SaleMasterListSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    customer_address = serializers.ReadOnlyField(source='customer.address', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    # order_no = serializers.ReadOnlyField(source='ref_order_master.order_no', allow_null=True)

    class Meta:
        model = SaleMaster
        fields = ['id','sale_no','customer_first_name','customer_middle_name','customer_last_name','customer_address','created_by_user_name']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class SaleDetailListSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='sale_master.customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='sale_master.customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='sale_master.customer.last_name', allow_null=True)
    sale_no=serializers.ReadOnlyField(source='sale_master.sale_no', allow_null=True)
    
    class Meta:
        model = SaleDetail
        fields = ['id','sale_master','sale_no','item','item_name','customer_first_name','customer_middle_name','customer_last_name']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']



class GetCustomerSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Customer
        fields = ['id','first_name','middle_name','last_name','address','phone_no']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']



class GetRepairDetailSerializer(serializers.ModelSerializer):
    repair_status = GetRepairUserSerializer(many=True, read_only=True)
    repair_item_name =  serializers.ReadOnlyField(source='item.name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale.sale_no', allow_null=True)
    sale_date = serializers.ReadOnlyField(source= 'sale.created_date_ad', allow_null=True, default="")
    assigned_to_user_name = serializers.ReadOnlyField(source= 'assigned_to.user_name', allow_null=True, default="")
    # repair_status_display= serializers.ReadOnlyField(source='get.repair_guy_repair_status_display', allow_null=True)

    class Meta:
        model = RepairDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']
    
    # def to_representation(self, instance):
    #     data =  super().to_representation(instance)
    #     if data['repair_guy']  is not None:
    #         repair_guy = RepairUser.objects.get(id=data["repair_guy"])
    #         repair_guy_data = GetRepairUserSerializer(repair_guy)
    #         data['repair_guy'] =  repair_guy_data.data
    #     return data
  

class RepairListSerializer(serializers.ModelSerializer):
    repair_details = GetRepairDetailSerializer(many=True, read_only=True)
    repair_status_display=serializers.ReadOnlyField(source='get_repair_status_display', allow_null=True)
    class Meta:
        model = Repair
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


    def to_representation(self, instance):
        data =  super().to_representation(instance)
        if data['customer']  is not None:
            customer = Customer.objects.get(id=data["customer"])
            customer_data = GetCustomerSerializer(customer)
            data['customer'] =  customer_data.data
        return data


