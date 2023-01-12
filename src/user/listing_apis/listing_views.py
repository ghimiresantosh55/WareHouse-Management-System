from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from src.user_group.models import CustomGroup

from ..user_permissions import UserListPermission
from .listing_serializers import GroupsCustomerListSerializer, DepartmentUserListSerializer
from ...department.models import Department


class GroupListApiView(ListAPIView):
    permission_classes = [UserListPermission]
    queryset = CustomGroup.objects.filter(is_active=True)
    serializer_class = GroupsCustomerListSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class DepartmentListApiView(ListAPIView):
    permission_classes = [UserListPermission]
    queryset = Department.objects.all()
    serializer_class = DepartmentUserListSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name']
