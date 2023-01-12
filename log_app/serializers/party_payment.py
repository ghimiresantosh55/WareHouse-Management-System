from rest_framework import serializers
from src.party_payment.models import PartyPayment, PartyPaymentDetail

from django.db import connections, models
from rest_framework.fields import SerializerMethodField
from tenant.utils import tenant_schema_from_request
from src.user.models import User


class PartyPaymentHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    class Meta:
        model = PartyPayment.history.model
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


class PartyPaymentDetailHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    class Meta:
        model = PartyPaymentDetail.history.model
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