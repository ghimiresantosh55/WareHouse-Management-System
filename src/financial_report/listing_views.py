from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.financial_report.serializer.listing_serializers import ReportUserListSerializer, ReportCustomerListSerializer, \
    ReportSupplierListSerializer, \
    ReportSaleListSerializer, ReportPurchaseReceivedListSerializer, ReportItemListSerializer
from src.user.models import User
from ..customer.models import Customer
from ..item.models import Item
from ..purchase.models import PurchaseMaster
from ..sale.models import SaleMaster
from ..supplier.models import Supplier


class ReportUserListApiView(ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'user_name']
    serializer_class = ReportUserListSerializer

    def get_queryset(self):
        return User.objects.filter(is_active=True).values("id", "user_name", "first_name", "last_name")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class ReportItemListAPIView(ListAPIView):
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['code', 'name']
    filter_fields = ['id', 'name']
    serializer_class = ReportItemListSerializer

    def get_queryset(self):
        return Item.objects.filter(active=True).values('id', 'code', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class ReportSupplierListApiView(ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    serializer_class = ReportSupplierListSerializer

    def get_queryset(self):
        return Supplier.objects.filter(active=True).values("id", "name")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class ReportCustomerListApiView(ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'user__user_name']
    serializer_class = ReportCustomerListSerializer

    def get_queryset(self):
        return Customer.objects.filter(active=True).values("id", "first_name", "middle_name", "last_name", 'user')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class ReportSaleListApiView(ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id', 'sale_no']
    serializer_class = ReportSaleListSerializer

    def get_queryset(self):
        return SaleMaster.objects.filter(active=True).values("id", "sale_no")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class ReportPurchaseNoListApiView(ListAPIView):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id', 'purchase_no']
    serializer_class = ReportPurchaseReceivedListSerializer

    def get_queryset(self):
        return PurchaseMaster.objects.filter(purchase_type=1).values("id", "purchase_no")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
