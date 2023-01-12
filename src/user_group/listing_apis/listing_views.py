from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from src.user_group.models import CustomPermission, PermissionCategory

from ..group_permissions import GroupListPermission
from .listing_serializers import GroupCustomPermissionListSerializer, GroupPermissionCategoryListSerializer


class PermissionListApiView(ListAPIView):
    permission_classes = [GroupListPermission]
    queryset = CustomPermission.objects.filter()
    serializer_class = GroupCustomPermissionListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    filter_fields = ['category']


class PermissionCategoryListApiView(ListAPIView):
    permission_classes = [GroupListPermission]
    queryset = PermissionCategory.objects.filter()
    serializer_class = GroupPermissionCategoryListSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
