import django_filters
from django.db import connection
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.core_app.models import DiscountScheme
from src.customer.models import Customer
from src.item.models import Item
from tenant.models import Tenant
from tenant.utils import tenant_schema_from_request
from .listing_serializers import (CustomerCustomerOrderListSerializer,
                                  DiscountSchemeCustomerOrderListSerializer, ItemCustomerOrderListSerializer,
                                  SelfCustomerOrderListSerializer, TransferBranchListSerializer)
from ..models import OrderMaster
from ...item.services.stock_item_info import get_remaining_sold_purchased_item


class CustomerListApiView(ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerCustomerOrderListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'middle_name', 'last_name', 'pan_vat_no']
    ordering_fields = ['id', 'first_name']


class DiscountSchemeListApiView(ListAPIView):
    queryset = DiscountScheme.objects.all()
    serializer_class = DiscountSchemeCustomerOrderListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class ItemListFilterForCustomerOrder(django_filters.FilterSet):
    id = django_filters.ModelMultipleChoiceFilter(queryset=Item.objects.filter(active=True),
                                                  to_field_name='id')

    class Meta:
        model = Item
        fields = ['id', 'name']


class ItemListApiView(ListAPIView):
    serializer_class = ItemCustomerOrderListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = ItemListFilterForCustomerOrder
    search_fields = ['name']
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        queryset = get_remaining_sold_purchased_item()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class SelfCustomerOrderListAPIView(ListAPIView):
    serializer_class = SelfCustomerOrderListSerializer
    pagination_class = None

    def get_queryset(self):
        if self.request.user:
            return OrderMaster.objects.filter(created_by=self.request.user).order_by('-created_date_ad')[:5]
        return OrderMaster.objects.none()

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset().order_by('-id')
    #
    #     page = queryset[:5]
    #     return Response(page, status=status.HTTP_200_OK)


class TransferBranchListAPIView(ListAPIView):
    serializer_class = TransferBranchListSerializer
    permission_classes = [AllowAny]
    queryset = Tenant.objects.all()

    def list(self, request, *args, **kwargs):
        connection.cursor().execute(f"SET search_path to public")

        queryset = self.filter_queryset(Tenant.objects.exclude(schema_name=tenant_schema_from_request(request)))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransferBranchListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
