from django.db import transaction
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.response import Response

from src.item_serialization.models import PackingTypeCode
from .location_serializer import (
    GetLocationPurchaseOrderDetailsSerializer, UpdateLocationPurchaseOrderDetailSerializer,
    GetLocationDirectPurchaseDetailsSerializer, UpdateLocationDirectPurchaseDetailSerializer,
    UpdateBulkLocationPurchaseOrderDetailSerializer, UpdateBulkLocationDirectPurchaseDetailSerializer,
)
from .models import PurchaseOrderDetail, PurchaseDetail
from .purchase_permissions import PurchaseOrderUpdateLocationPermission, PurchaseUpdateLocationPermission


class UpdateLocationPurchaseOrderDetailView(ListCreateAPIView):
    permission_classes = [PurchaseOrderUpdateLocationPermission]
    queryset = PurchaseOrderDetail.objects.filter(purchase_order__order_type=3).distinct().prefetch_related(
        Prefetch('po_pack_type_codes',
                 queryset=PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True).order_by(
                     'id').select_related('location'))).select_related('item',
                                                                       'item_category',
                                                                       'packing_type')
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['purchase_order', 'item', 'item_category', 'id']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            serializer_class = UpdateLocationPurchaseOrderDetailSerializer
        elif self.request.method == 'GET':
            serializer_class = GetLocationPurchaseOrderDetailsSerializer

        return serializer_class

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateBulkLocationPurchaseOrderDetailView(CreateAPIView):
    permission_classes = [PurchaseOrderUpdateLocationPermission]
    queryset = PurchaseOrderDetail.objects.filter(purchase_order__order_type=3).distinct().prefetch_related(
        Prefetch('po_pack_type_codes',
                 queryset=PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True).order_by(
                     'id').select_related('location'))).select_related('item',
                                                                       'item_category',
                                                                       'packing_type')
    serializer_class = UpdateBulkLocationPurchaseOrderDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['purchase_order', 'item', 'item_category', 'id']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateLocationDirectPurchaseDetailView(ListCreateAPIView):
    permission_classes = [PurchaseUpdateLocationPermission]
    queryset = PurchaseDetail.objects.filter(purchase__purchase_type=1,
                                             purchase__ref_purchase_order__isnull=True).distinct().prefetch_related(
        Prefetch('pu_pack_type_codes',
                 queryset=PackingTypeCode.objects.order_by('id').select_related('location'))
    ).select_related('item',
                     'item_category',
                     'packing_type')
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['purchase', 'item', 'item_category', 'id']

    def get_serializer_class(self):
        serializer_class = GetLocationDirectPurchaseDetailsSerializer
        if self.request.method == 'POST':
            serializer_class = UpdateLocationDirectPurchaseDetailSerializer

        return serializer_class

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateBulkLocationDirectPurchaseDetailView(CreateAPIView):
    permission_classes = [PurchaseUpdateLocationPermission]
    queryset = PurchaseDetail.objects.filter(purchase__purchase_type=1,
                                             purchase__ref_purchase_order__isnull=True).distinct().prefetch_related(
        Prefetch('pu_pack_type_codes',
                 queryset=PackingTypeCode.objects.order_by('id').select_related('location'))
    ).select_related('item',
                     'item_category',
                     'packing_type')
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['purchase', 'item', 'item_category', 'id']
    serializer_class = UpdateBulkLocationDirectPurchaseDetailSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
