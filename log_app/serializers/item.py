from django.db import connections
from django_filters.filters import _truncate
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField, SerializerMethodField
from src.item.models import Unit, Manufacturer, GenericName, ItemCategory, PackingType, Item
# from simple_history.tests.models import Poll
from rest_framework import serializers
from tenant.utils import tenant_schema_from_request

from src.user.models import User


class UnitHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    class Meta:
        model = Unit.history.model
        exclude = ['history_date']
    def get_history_user_name(self,unit):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=unit.history_user_id).user_name
                return user_name
            except:
                return None


class PackingTypeHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    class Meta:
        model = PackingType.history.model
        exclude = ['history_date']
    def get_history_user_name(self,unit):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=unit.history_user_id).user_name
                return user_name
            except:
                return None


class ManufacturerHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()

    class Meta:
        model = Manufacturer.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,unit):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=unit.history_user_id).user_name
                return user_name
            except:
                return None


class GenericNameHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()

    class Meta:
        model = GenericName.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,unit):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=unit.history_user_id).user_name
                return user_name
            except:
                return None


class ItemCategoryHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()

    class Meta:
        model = ItemCategory.history.model
        exclude = ['history_date']
    
    def get_history_user_name(self,item_category):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                user_name = User.objects.get(id=item_category.history_user_id).user_name
                return user_name
            except:
                return None
    

class ItemHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    history_user_name = SerializerMethodField()
    item_category_name = SerializerMethodField()
    
    class Meta:
        model = Item.history.model
        exclude = ['history_date']
    
    def get_item_category_name(self,item):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        # print(schema)
        # print(item.item_category_id)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = ItemCategory.objects.get(id=item.item_category_id).name
                return category_name
            except:
                return None

    
    def get_history_user_name(self,item):
        request = self.context.get('request')
        schema = tenant_schema_from_request(request)
        with connections['default'].cursor() as c:
            c.execute(f'SET search_path to {schema}')
            try:
                category_name = User.objects.get(id=item.history_user_id).user_name
                return category_name
            except:
                return None
