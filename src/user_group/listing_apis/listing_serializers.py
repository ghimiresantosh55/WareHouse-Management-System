from rest_framework import serializers

from rest_framework import serializers

from ..models import CustomPermission, PermissionCategory


class GroupPermissionCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionCategory
        fields = ['id', 'name']


class GroupCustomPermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ['id', 'name', 'code_name', 'category']
