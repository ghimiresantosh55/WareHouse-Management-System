
from django.utils import timezone
from rest_framework import serializers
from src.customer.models import Customer
from src.custom_lib.functions import current_user
from src.repair.models import Repair,RepairDetail,  RepairUser
from src.custom_lib.functions.current_user import get_created_by
# from .listing_apis.serializers import GetCustomerSerializer
# from .listing_apis.serializers import ListCustomerSerializer



class ListCustomerSerializer(serializers.ModelSerializer):
   '''
   listing serializer for customer
   '''
   class Meta:
        model = Customer
        fields = ['id','first_name','middle_name','last_name','address','phone_no']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']



class SaveRepairDetailSerializer(serializers.ModelSerializer):
    '''
    model serializer for repair detail 
    '''
    # repair_status = GetRepairUserSerializer(many=True, read_only=True)
    repair_item_name =  serializers.ReadOnlyField(source='item.name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale.sale_no', allow_null=True)
    sale_date = serializers.ReadOnlyField(source= 'sale.created_date_ad', allow_null=True, default="")
   

    class Meta:
        model = RepairDetail
        exclude = ["repair"]
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs','device_type','app_type']


class RepairDetailSerializer(serializers.ModelSerializer):
    '''
    model serializer for repair detail
    '''
    repair_item_name =  serializers.ReadOnlyField(source='item.name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale.sale_no', allow_null=True)
    sale_date = serializers.ReadOnlyField(source= 'sale.created_date_ad', allow_null=True, default="")
    
    class Meta:
        model = RepairDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs','device_type','app_type']



class RepairSerializer(serializers.ModelSerializer):
    '''
    model serializer for repair
    '''
    repair_details =SaveRepairDetailSerializer(many=True)
    repair_status_display=serializers.ReadOnlyField(source='get_repair_status_display', allow_null=True)
    class Meta:
        model = Repair
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs','device_type','app_type']
    

    def to_representation(self, instance):
        '''
        to representation for  get customer object
        '''
        data =  super().to_representation(instance)
        if data['customer']  is not None:
            customer = Customer.objects.get(id=data["customer"])
            customer_data =  ListCustomerSerializer(customer)
            data['customer'] =  customer_data.data
        return data


    def create(self, validated_data):
        '''
        create method for repair
        '''
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        repair_details = validated_data.pop('repair_details')
        repair = Repair.objects.create(**validated_data, created_date_ad=date_now)
        for repair_detail in repair_details:
       
            repair_detail=RepairDetail.objects.create(**repair_detail, repair=repair,
                                          created_by=validated_data['created_by'], created_date_ad=date_now)

            RepairUser.objects.create(repair_detail=repair_detail,repair_status=1, created_date_ad=date_now, created_by=current_user.get_created_by(self.context))
        return repair


class RepairUserSerializer(serializers.ModelSerializer):
    '''
    model serializer for repair user
    '''
    repair_customer_id=serializers.ReadOnlyField(source='repair_detail.repair.customer.id', allow_null=True, default="")
    repair_item = serializers.ReadOnlyField(source='repair_detail.item.name', allow_null=True, default="")
    repair_problem_description=serializers.ReadOnlyField(source='repair_detail.problem_description', allow_null=True, default="")
    repair_status_display=serializers.ReadOnlyField(source='get_repair_status_display', allow_null=True)
    created_by_user_name= serializers.ReadOnlyField(source='created_by.user_name', allow_null=True, default="")

    class Meta:
        model = RepairUser
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs','device_type','app_type']


    def create(self, validated_data):
        '''
        create method for repair user
        '''
        validated_data['created_by'] = get_created_by(self.context)
        date_now = timezone.now()
        repair_user= RepairUser.objects.create(**validated_data, created_date_ad=date_now)
        return repair_user

       

      