from django.db import connections, models
from rest_framework import fields, serializers

# models
from src.advance_deposit.models import AdvancedDeposit ,AdvancedDepositPaymentDetail

from rest_framework.fields import SerializerMethodField
from tenant.utils import tenant_schema_from_request
from src.user.models import User

class AdvancedDepositHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = fields.SerializerMethodField()
    class Meta:
        model = AdvancedDeposit.history.model
        exclude = ['history_date']
    
    # def get_purchase_bill_no(self,purchasedetail):
    #     request = self.context.get('request')
    #     schema = tenant_schema_from_request(request)
    #     # print(purchasedetail.purchase_id)
    #     with connections['default'].cursor() as c:
    #         c.execute(f'SET search_path to {schema}')
    #         try:
    #             bill_no = PurchaseMaster.objects.get(id=purchasedetail.purchase_id).purchase_no
    #             return bill_no
    #         except:
    #             return None
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
            


class AdvancedDepositPaymentDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    
    class Meta:
        model = AdvancedDepositPaymentDetail.history.model
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
    