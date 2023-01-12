from django.db import models
from rest_framework import serializers

from rest_framework import serializers
from src.core_app.models import Country
from src.customer.models import Customer

from django.db import connections, models
from rest_framework.fields import SerializerMethodField
from tenant.utils import tenant_schema_from_request
from src.user.models import User

class CustomerHistoryListView(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    first_name = SerializerMethodField()
    middle_name = SerializerMethodField()
    last_name = SerializerMethodField()
    country_name = SerializerMethodField()
    class Meta:
        model = Customer.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,customer):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=customer.history_user_id).user_name
                return user_name
            except:
                return None
    
    def get_first_name(self,customer):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                first_name = User.objects.get(id=customer.history_user_id).first_name
                return first_name
            except:
                return None
    
    def get_middle_name(self,customer):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                middle_name = User.objects.get(id=customer.history_user_id).middle_name
                return middle_name
            except:
                return None
    
    def get_last_name(self,customer):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                last_name = User.objects.get(id=customer.history_user_id).last_name
                return last_name
            except:
                return None
    
    def get_country_name(self,customer):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                country_name = Country.objects.get(id=customer.country_id).name
                return country_name
            except:
                return None