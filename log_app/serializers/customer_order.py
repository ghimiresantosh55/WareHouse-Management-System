from rest_framework import fields, serializers
from src.customer_order.models import OrderMaster,OrderDetail

from django.db import connections, models
from rest_framework.fields import SerializerMethodField
from tenant.utils import tenant_schema_from_request
from src.user.models import User


class OrderMasterHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    class Meta:
        model = OrderMaster.history.model
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
      

class OrderDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    class Meta:
        model = OrderDetail.history.model
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

    


