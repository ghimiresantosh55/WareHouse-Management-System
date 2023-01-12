from rest_framework import serializers

from src.department.models import Department
from django.utils import timezone


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'allow_sales',
                  'created_date_ad', 'created_date_bs']
        read_only_fields = ['created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        department = Department.objects.create(
            **validated_data,
            created_date_ad=timezone.now()
        )

        return department
