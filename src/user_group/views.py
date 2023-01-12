import django_filters
from django_filters.rest_framework import DateFromToRangeFilter, DjangoFilterBackend, FilterSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from .group_permissions import GroupPermission, PermissionCategoryPermission, PermissionPermission
from .models import CustomGroup, CustomPermission, PermissionCategory
from .serializers import CustomGroupSerializer, CustomPermissionSerializer, PermissionCategorySerializer


class FilterForCustomGroup(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = CustomGroup
        fields = ['is_active', 'id',
                  'date', 'name']


class CustomGroupViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'post', 'patch']
    permission_classes = [GroupPermission]
    queryset = CustomGroup.objects.all()
    serializer_class = CustomGroupSerializer
    filter_class = FilterForCustomGroup
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class CustomPermissionViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'post', 'patch']
    permission_classes = [PermissionPermission]
    queryset = CustomPermission.objects.all()
    serializer_class = CustomPermissionSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code_name']
    ordering_fields = ['id', 'name']
    filter_fields = ['id', 'category']


class PermissionCategoryViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'post', 'patch']
    permission_classes = [PermissionCategoryPermission]
    queryset = PermissionCategory.objects.all()
    serializer_class = PermissionCategorySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    filter_fields = ['id']
