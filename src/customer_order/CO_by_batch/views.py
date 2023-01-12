import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response

from src.customer_order.models import OrderDetail
from src.customer_order.models import OrderMaster
from src.item_serialization.services import pack_and_serial_info
from src.purchase.models import PurchaseDetail
from .list_serializers import GetStockByBatchListSerializer, GetPackTypeDetailByBatchSerializer, \
    GetPackTypeByBatchSerializer
from .serializers import (SaveCustomerOrderByBatchSerializer,
                          SaveAndVerifyCustomerPackingTypesSerializer, UpdateCustomerOrderByBatchSerializer,
                          UpdateCustomerDetailsByBatchSerializer)
from ...item.models import Item
from ...item_serialization.models import PackingTypeCode
from ...purchase.services.stock_analysis import get_batch_stock


class ByBatchItemListFilter(django_filters.FilterSet):
    item = django_filters.ModelMultipleChoiceFilter(queryset=Item.objects.filter(active=True),
                                                    to_field_name='id')
    exclude_id = django_filters.ModelMultipleChoiceFilter(queryset=PurchaseDetail.objects.
                                                          filter(ref_purchase_detail__isnull=True),
                                                          to_field_name='id', exclude=True)

    class Meta:
        model = PurchaseDetail
        fields = ['item', 'id', 'exclude_id']


class GetStockByBatchListViewSet(ListAPIView):
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ['batch_no']
    ordering_fields = ['id']
    filter_class = ByBatchItemListFilter
    serializer_class = GetStockByBatchListSerializer

    def get_queryset(self):
        return get_batch_stock()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class GetPackTypeByBatchFilterSet(django_filters.FilterSet):
    location_code = django_filters.CharFilter(field_name='location__code')

    class Meta:
        model = PackingTypeCode
        fields = ['purchase_detail', 'location_code']


class GetPackTypeByBatchRetrieveApiView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filter_class = GetPackTypeByBatchFilterSet
    serializer_class = GetPackTypeByBatchSerializer

    def get_queryset(self):
        queryset = pack_and_serial_info.find_available_serializable_pack()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class GetPackTypeDetailByBatchRetrieveApiView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['pack_type_code', 'code']
    serializer_class = GetPackTypeDetailByBatchSerializer

    def get_queryset(self):
        queryset = pack_and_serial_info.find_available_serial_nos()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class SaveCustomerOrderByBatchApiView(CreateAPIView):
    serializer_class = SaveCustomerOrderByBatchSerializer
    queryset = OrderMaster.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(SaveCustomerOrderByBatchApiView, self).create(request, *args, **kwargs)


class SaveAndVerifyCustomerPackingTypesApiView(CreateAPIView):
    serializer_class = SaveAndVerifyCustomerPackingTypesSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = SaveAndVerifyCustomerPackingTypesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCustomerOrderByBatchAPIView(UpdateAPIView):
    queryset = OrderMaster.objects.filter(status=1, by_batch=True).select_related('customer',
                                                                                  'discount_scheme').prefetch_related(
        'order_details')
    serializer_class = UpdateCustomerOrderByBatchSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        order_details = request.data.pop('order_details')
        order_details_create = []
        for order_detail in order_details:
            if order_detail.get("id", False):
                order_detail_instance = OrderDetail.objects.get(id=order_detail['id'])

                serializer = UpdateCustomerDetailsByBatchSerializer(
                    order_detail_instance, data=order_detail, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                order_details_create.append(order_detail)

        request.data['order_details'] = order_details_create
        return super(UpdateCustomerOrderByBatchAPIView, self).partial_update(request, *args, **kwargs)
