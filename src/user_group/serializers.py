from rest_framework.serializers import ModelSerializer
from .models import CustomGroup, CustomPermission, PermissionCategory
from django.utils import timezone
from src.custom_lib.functions import current_user
from .models import CustomPermission


class CustomGroupSerializer(ModelSerializer):
    class Meta:
        model = CustomGroup
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        permissions = validated_data.pop('permissions')
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = CustomGroup.objects.create(**validated_data, created_date_ad=date_now)
        for permission in permissions:
            instance.permissions.add(permission)
        return instance



class CustomPermissionSerializer(ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = CustomPermission.objects.create(**validated_data, created_date_ad=date_now)
        return instance


class PermissionCategorySerializer(ModelSerializer):
    class Meta:
        model = PermissionCategory
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = PermissionCategory.objects.create(**validated_data, created_date_ad=date_now)
        return instance
