from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from .location_permissions import LocationPermission
from .models import Location
from .serializers import LocationCrateSerializer, LocationUpdateSerializer, LocationGetSerializer, \
    LocationMapSerializer, LocationItemListSerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    permission_classes = [LocationPermission]
    http_method_names = ['post', 'get', 'head', 'patch']
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name']
    filter_fields = ['id', 'name', 'parent', 'department']

    def get_serializer_class(self):
        serializer_class = LocationCrateSerializer
        if self.request.method == 'POST':
            serializer_class = LocationCrateSerializer
        elif self.request.method == 'GET':
            serializer_class = LocationGetSerializer
        elif self.request.method == 'PATCH':
            serializer_class = LocationUpdateSerializer
        return serializer_class


class LocationMapView(ListAPIView):
    serializer_class = LocationMapSerializer
    permission_classes = [LocationPermission]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name']
    filter_fields = ['id', 'name', 'department']

    def get_queryset(self):
        parent_ids = list(Location.objects.exclude(parent=None).values_list('parent', flat=True))
        queryset = Location.objects.exclude(id__in=parent_ids)
        return queryset


class LocationItemsListView(ListAPIView):
    serializer_class = LocationItemListSerializer
    permission_classes = [LocationPermission]

    def get_queryset(self):
        parent_ids = list(Location.objects.exclude(parent=None).values_list('parent', flat=True))
        queryset = Location.objects.exclude(id__in=parent_ids)
        return queryset
