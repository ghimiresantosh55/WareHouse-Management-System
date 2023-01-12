from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.core_app.models import Country
from .listing_serializers import CountrySupplierListSerializer, CustomerSupplierListSerializer
from ..supplier_permissions import SupplierPermission
from ...customer.models import Customer


class CountryListApiView(ListAPIView):
    permission_classes = [SupplierPermission]
    queryset = Country.objects.filter(active=True)
    serializer_class = CountrySupplierListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class CustomerListAPIView(ListAPIView):
    permission_classes = [SupplierPermission]
    serializer_class = CustomerSupplierListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'middle_name', 'last_name', 'pan_vat_no']
    ordering_fields = ['id', 'first_name']

    def get_queryset(self):
        return Customer.objects.filter(active=True).values('id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
