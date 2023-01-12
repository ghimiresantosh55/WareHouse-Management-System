from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.core_app.models import AdditionalChargeType, Country, DiscountScheme, PaymentMode, Currency
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail
from src.purchase.models import PurchaseDocumentType, PurchaseMaster, PurchaseOrderMaster
from src.supplier.models import Supplier
from .listing_serializers import (PurchaseAdditionalChargeTypeListSerializer, PurchaseCurrencyListSerializer,
                                  PurchaseDiscontSchemeListSerializer, PurchaseItemCategoryListSerializer,
                                  PurchaseItemListSerializer, PurchasePackingTypeDetailListSerializer,
                                  PurchasePackingTypeListSerializer, PurchasePaymentModeListSerializer,
                                  PurchasePurchaseDocumentTypeListSerializer, PurchaseSupplierListSerializer,
                                  PurchaseCountryListSerializer, PurchaseNoListSerializer,
                                  PurchaseOrderNoListSerializer, PurchaseDepartmentListSerializer)
from ..purchase_permissions import PurchasePermission, PurchaseOrderReceivePermission
from ...department.models import Department


class CountryListApiView(ListAPIView):
    # permission_classes = [ItemListPermission]
    queryset = Country.objects.filter(active=True)
    serializer_class = PurchaseCountryListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class CurrencyListAPIView(ListAPIView):
    # permission_classes = [ItemListPermission]
    queryset = Currency.objects.filter(active=True)
    serializer_class = PurchaseCurrencyListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'symbol', 'code']


class DiscountSchemeListApiView(ListAPIView):
    # permission_classes = [ItemListPermission]
    queryset = DiscountScheme.objects.filter(active=True)
    serializer_class = PurchaseDiscontSchemeListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class ItemCategoryListApiView(ListAPIView):
    # permission_classes = [ItemListPermission]
    queryset = ItemCategory.objects.filter(active=True)
    serializer_class = PurchaseItemCategoryListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


class PackingTypeListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = PackingType.objects.filter(active=True)
    serializer_class = PurchasePackingTypeListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'short_name']
    ordering_fields = ['id', 'name', 'short_name']


class ItemListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = Item.objects.filter(active=True)
    serializer_class = PurchaseItemListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


class SupplierListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = Supplier.objects.filter(active=True)
    serializer_class = PurchaseSupplierListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class PackingTypeDetailListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = PackingTypeDetail.objects.filter(active=True).select_related('packing_type')
    serializer_class = PurchasePackingTypeDetailListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id']
    filter_fields = ['item', 'packing_type']


class PurchaseDocumentTypeListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = PurchaseDocumentType.objects.filter(active=True)
    serializer_class = PurchasePurchaseDocumentTypeListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class PaymentModeListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = PaymentMode.objects.filter(active=True)
    serializer_class = PurchasePaymentModeListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class AdditionalChargeListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    queryset = AdditionalChargeType.objects.filter(active=True)
    serializer_class = PurchaseAdditionalChargeTypeListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class DepartmentListApiView(ListAPIView):
    # permission_classes = [PackTypeDetailListPermission]
    serializer_class = PurchaseDepartmentListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'code']

    def get_queryset(self):

        return self.request.user.departments.filter(allow_sales=True)


class PurchaseNoListApiView(ListAPIView):
    permission_classes = [PurchasePermission]
    serializer_class = PurchaseNoListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'purchase_no']
    ordering_fields = ['id']
    filter_fields = ['id', 'purchase_no']

    def get_queryset(self):
        return PurchaseMaster.objects.filter(purchase_type=1,
                                             purchasemaster__purchase_type=2).values('id', 'purchase_no')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class PurchaseOrderNoListAPIView(ListAPIView):
    permission_classes = [PurchaseOrderReceivePermission]
    serializer_class = PurchaseOrderNoListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'order_no']
    ordering_fields = ['id']
    filter_fields = ['id', 'order_no']

    def get_queryset(self):
        return PurchaseOrderMaster.objects.filter(order_type=1,
                                                  self_purchase_order_master__order_type=3).values('id', 'order_no')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
