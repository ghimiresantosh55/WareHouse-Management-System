import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.core_app.models import AdditionalChargeType, DiscountScheme, PaymentMode
from src.customer.models import Customer
from src.item_serialization.models import PackingTypeCode
from .listing_serializers import (AdditionalChargeTypeSaleListSerializer, CustomerSaleListSerializer,
                                  DiscoutnSchemeSaleListSerializer, PaymentModeSaleListSerializer, SaleNoListSerializer,
                                  GetPackTypeDetailSerializer, GetPackTypeByCodeSerializer)
from ..models import SaleMaster
from ..sale_permissions import SalePermission
from ...item_serialization.services import pack_and_serial_info


class CustomerListApiView(ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSaleListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'middle_name', 'last_name', 'pan_vat_no']
    ordering_fields = ['id', 'first_name']


class DiscountSchemeListApiView(ListAPIView):
    queryset = DiscountScheme.objects.all()
    serializer_class = DiscoutnSchemeSaleListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class PaymentModeListApiView(ListAPIView):
    queryset = PaymentMode.objects.filter(active=True)
    serializer_class = PaymentModeSaleListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class AdditionalChargeTypeListApiView(ListAPIView):
    queryset = AdditionalChargeType.objects.filter(active=True)
    serializer_class = AdditionalChargeTypeSaleListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class SaleNoListAPIView(ListAPIView):
    permission_classes = [SalePermission]
    serializer_class = SaleNoListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'sale_no']
    ordering_fields = ['id']
    filter_fields = ['id', 'sale_no']

    def get_queryset(self):
        return SaleMaster.objects.filter(sale_type=1,
                                         salemaster__sale_type=2).values('id', 'sale_no')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class GetPackTypeByBatchFilterSet(django_filters.FilterSet):
    class Meta:
        model = PackingTypeCode
        fields = ['code', 'id']


class GetPackTypeByCodeApiView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filter_class = GetPackTypeByBatchFilterSet
    serializer_class = GetPackTypeByCodeSerializer

    def get_queryset(self):
        queryset = pack_and_serial_info.find_available_serializable_pack()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class GetPackTypeDetailApiView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['pack_type_code', 'code']
    serializer_class = GetPackTypeDetailSerializer

    def get_queryset(self):
        queryset = pack_and_serial_info.find_available_serial_nos()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
