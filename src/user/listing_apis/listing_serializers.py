from src.department.models import Department
from src.user_group.models import CustomGroup
from rest_framework import serializers


class GroupsCustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomGroup
        fields = ['id', 'name']


class DepartmentUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']
