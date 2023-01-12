from django.db import models
from rest_framework import fields, serializers
from src.core_app.models import AdditionalChargeType, PaymentMode
from src.item.models import Item, ItemCategory
from src.sale.models import SaleMaster, SaleDetail, SalePaymentDetail, SaleAdditionalCharge ,SalePrintLog

from django.db import connections, models
from rest_framework.fields import ReadOnlyField, SerializerMethodField
from src.customer.models import Customer
from tenant.utils import tenant_schema_from_request
from src.user.models import User


class SaleMasterHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    customer_name = SerializerMethodField()
    sale_type_display = ReadOnlyField(source="get_sale_type_display", allow_null=True)
    pay_type_display = ReadOnlyField(source="get_pay_type_display", allow_null=True)

    class Meta:
        model= SaleMaster.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,sale_master):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = User.objects.get(id=sale_master.history_user_id).user_name
                return category_name
            except:
                return None
    
    def get_customer_name(self,sale_master):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                first_name = Customer.objects.get(id=sale_master.customer_id).first_name
                return first_name
            except:
                return None
    


class SaleDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    item_category_name = SerializerMethodField()
    item_name = SerializerMethodField()
    class Meta:
        model= SaleDetail.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,sale_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=sale_detail.history_user_id).user_name
                return user_name
            except:
                return None
    
    def get_item_name(self,sale_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            item_name = Item.objects.get(id=sale_detail.item_id).name
        return item_name
    
    def get_item_category_name(self,sale_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            category_name = ItemCategory.objects.get(id=sale_detail.item_category_id).name
        return category_name


class SalePaymentDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    sale_master_sale_no = SerializerMethodField()
    payment_mode_name = SerializerMethodField()
    class Meta:
        model= SalePaymentDetail.history.model
        exclude = ['history_date']

    def get_history_user_name(self,advancedeposite):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = User.objects.get(id=advancedeposite.history_user_id).user_name
                return category_name
            except:
                return None
    
    def get_sale_master_sale_no(self,payment_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                sale_no = SaleMaster.objects.get(id=payment_detail.sale_master_id).sale_no
                return sale_no
            except:
                return None
    
    def get_payment_mode_name(self,payment_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                payment_mode_name = PaymentMode.objects.get(id=payment_detail.payment_mode_id).name
                return payment_mode_name
            except:
                return None

class SaleAdditionalChargeHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    charge_type_name = SerializerMethodField()
    sale_master_sale_no = SerializerMethodField()
    class Meta:
        model= SaleAdditionalCharge.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,additional_charge):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=additional_charge.history_user_id).user_name
                return user_name
            except:
                return None
    
    def get_charge_type_name(self,additional_charge):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = AdditionalChargeType.objects.get(id=additional_charge.charge_type_id).name
                return category_name
            except:
                return None
    
    def get_sale_master_sale_no(self,additional_charge):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                sale_no = SaleMaster.objects.get(id=additional_charge.sale_master_id).sale_no
                return sale_no
            except:
                return None

class SalePrintLogHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    class Meta:
        model= SalePrintLog.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,additional_charge):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = User.objects.get(id=additional_charge.history_user_id).user_name
                return category_name
            except:
                return None