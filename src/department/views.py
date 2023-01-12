from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from .department_permissions import DepartmentPermission
from .models import Department
from .serializers import DepartmentSerializer


class DepartmentModelViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [DepartmentPermission]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']
    filterset_fields = ['name', 'code']
    http_method_names = ['get', 'post', 'patch']
