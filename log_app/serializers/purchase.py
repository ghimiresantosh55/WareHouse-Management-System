from src.core_app.models import AdditionalChargeType, PaymentMode
from log_app.views import purchase
from rest_framework import serializers
from src.item.models import Item, ItemCategory
from src.purchase.models import PurchaseOrderMaster, PurchaseOrderDetail,\
    PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge


from django.db import connections, models
from rest_framework.fields import ReadOnlyField, SerializerMethodField
from src.supplier.models import Supplier
from tenant.utils import tenant_schema_from_request
from src.user.models import User


class PurchaseOrderMasterHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    supplier_name = SerializerMethodField()
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)
    # ref_purchase_order_order_no = SerializerMethodField()
    class Meta:
        model = PurchaseOrderMaster.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,purchase_order):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=purchase_order.history_user_id).user_name
                return user_name
            except:
                return None

    def get_supplier_name(self,purchase_order):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                first_name = Supplier.objects.get(id=purchase_order.supplier_id).first_name
                return first_name
            except:
                return None
    
    
    # def get_ref_purchase_order_order_no(self,purchase_order):
    #     request = self.context.get('request')
    #     schema = tenant_schema_from_request(request)
    #     with connections['default'].cursor() as c:
    #         c.execute(f'SET search_path to {schema}')
    #         try:
    #             user_name = PurchaseOrderMaster.objects.get(id=purchase_order.ref_purchase_order_id).order_no
    #             return user_name
    #         except:
    #             return None


class PurchaseOrderDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    purchase_order_bill_no = SerializerMethodField()
    item_name = SerializerMethodField()
    item_category_name = SerializerMethodField()
    history_user_name = SerializerMethodField()

    class Meta:
        model = PurchaseOrderDetail.history.model
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

    def get_purchase_order_bill_no(self,purchaseorder):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            category_name = PurchaseOrderMaster.objects.get(id=purchaseorder.purchase_order_id).order_no
        return category_name
    
    def get_item_name(self,purchaseorder):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            item_name = Item.objects.get(id=purchaseorder.item_id).name
        return item_name
    
    def get_item_category_name(self,purchaseorder):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            category_name = ItemCategory.objects.get(id=purchaseorder.item_category_id).name
        return category_name
    

class PurchaseMasterHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    supplier_name = SerializerMethodField()
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    
    class Meta:
        model = PurchaseMaster.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,purchase_master):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = User.objects.get(id=purchase_master.history_user_id).user_name
                return category_name
            except:
                return None
    
    def get_supplier_name(self,purchase_master):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                first_name = Supplier.objects.get(id=purchase_master.supplier_id).first_name
                return first_name
            except:
                return None
    
    


class PurchaseDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    purchase_bill_no= SerializerMethodField()
    item_category_name= SerializerMethodField()
    item_name= SerializerMethodField()
    history_user_name = SerializerMethodField()
    class Meta:
        model = PurchaseDetail.history.model
        exclude = ['history_date']
    
    def get_item_category_name(self,purchase_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            item_category_name = Item.objects.get(id=purchase_detail.item_category_id).name
        return item_category_name

    def get_item_name(self,purchase_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            item_name = Item.objects.get(id=purchase_detail.item_id).name
        return item_name
    
    def get_history_user_name(self,purchase_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = User.objects.get(id=purchase_detail.history_user_id).user_name
                return category_name
            except:
                return None

    def get_purchase_bill_no(self,purchasedetail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        # print(purchasedetail.purchase_id)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                bill_no = PurchaseMaster.objects.get(id=purchasedetail.purchase_id).purchase_no
                return bill_no
            except:
                return None


class PurchasePaymentDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    purchase_master_purchase_no = SerializerMethodField()
    payment_mode_name = SerializerMethodField()
    class Meta:
        model = PurchasePaymentDetail.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,payment_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = User.objects.get(id=payment_detail.history_user_id).user_name
                return category_name
            except:
                return None
    
    def get_purchase_master_purchase_no(self,payment_detail):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                purchase_master_purchase_no = PurchaseMaster.objects.get(id=payment_detail.purchase_master_id).purchase_no
                return purchase_master_purchase_no
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


class PurchaseAdditionalChargeHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    charge_type_name = SerializerMethodField()
    purchase_master_purchase_no = SerializerMethodField()
    
    class Meta:
        model = PurchaseAdditionalCharge.history.model
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
    
    def get_charge_type_name(self,additional_charge):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                charge_type = AdditionalChargeType.objects.get(id=additional_charge.charge_type_id).name
                return charge_type
            except:
                return None
    
    def get_purchase_master_purchase_no(self,additional_charge):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                purchase_master = PurchaseMaster.objects.get(id=additional_charge.purchase_master_id).purchase_no
                return purchase_master
            except:
                return None
    

