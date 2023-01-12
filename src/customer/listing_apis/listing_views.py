from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import  status

from src.core_app.models import Country
from .listing_serializers import CountryCustomerListSerializer, SupplierCustomerListSerializer
from ..customer_permissions import CustomerPermission
from ...supplier.models import Supplier


class CountryListApiView(ListAPIView):
    permission_classes = [CustomerPermission]
    queryset = Country.objects.filter(active=True)
    serializer_class = CountryCustomerListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class SupplierListAPIView(ListAPIView):
    permission_classes = [CustomerPermission]
    serializer_class = SupplierCustomerListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        return Supplier.objects.filter(active=True).values('id', 'name', 'pan_vat_no')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
