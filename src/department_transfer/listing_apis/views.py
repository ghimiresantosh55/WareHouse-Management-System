import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.department.models import Department
from src.department.services.stocks import stock_by_department_queryset, get_department_batch_stock
from src.department_transfer.listing_apis.serializers import DepartmentTransferItemListSerializer, \
    DepartmentTransferDepartmentListSerializer, GetDepartmentStockByBatchListSerializer, \
    DepartmentTransferPackTypeCodesByBatchSerializer, DepartmentTransferPackTypeDetailListSerializer
from src.item.models import Item, PackingType, PackingTypeDetail
from src.item_serialization.models import PackingTypeCode
from src.item_serialization.services import pack_and_serial_info
from src.purchase.listing_apis.listing_serializers import PurchasePackingTypeListSerializer, \
    PurchasePackingTypeDetailListSerializer
from src.purchase.models import PurchaseDetail


class DepartmentTransferItemListView(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = DepartmentTransferItemListSerializer

    def list(self, request, *args, **kwargs):
        department = self.request.query_params.get('department', None)

        if not department:
            raise ValidationError({
                "department": "Missing query parameters "
            })
        queryset = stock_by_department_queryset(department)

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(queryset)


class DepartmentTransferFromDepartmentList(ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentTransferDepartmentListSerializer


class DepartmentTransferToDepartmentList(ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentTransferDepartmentListSerializer

    def list(self, request, *args, **kwargs):
        queryset = request.user.departments.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ByDepartmentBatchItemListFilter(django_filters.FilterSet):
    item = django_filters.ModelMultipleChoiceFilter(queryset=Item.objects.filter(active=True),
                                                    to_field_name='id')
    exclude_id = django_filters.ModelMultipleChoiceFilter(queryset=PurchaseDetail.objects.
                                                          filter(ref_purchase_detail__isnull=True),
                                                          to_field_name='id', exclude=True)

    class Meta:
        model = PurchaseDetail
        fields = ['item', 'id', 'exclude_id']


class GetDepartmentStockByBatchListViewSet(ListAPIView):
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ['batch_no']
    ordering_fields = ['id']
    filter_class = ByDepartmentBatchItemListFilter
    serializer_class = GetDepartmentStockByBatchListSerializer

    def get_queryset(self):
        return PurchaseDetail.objects.all()

    def list(self, request, *args, **kwargs):
        department = self.request.query_params.get('department', None)

        if not department:
            raise ValidationError({
                "department": "Missing query parameters "
            })
        queryset = get_department_batch_stock(department)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class PackingTypeListView(ListAPIView):
    queryset = PackingType.objects.all()
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'created_date_ad']
    search_fields = ['name']
    serializer_class = PurchasePackingTypeListSerializer


class PackingTypeDetailListView(ListAPIView):
    queryset = PackingTypeDetail.objects.all()
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'created_date_ad']
    filterset_fields = ['item', 'packing_type']
    serializer_class = PurchasePackingTypeDetailListSerializer


class DepartmentTransferPackTypeCodesByBatchFilterSet(django_filters.FilterSet):
    location_code = django_filters.CharFilter(field_name='location__code')

    class Meta:
        model = PackingTypeCode
        fields = ['purchase_detail', 'location_code']


class DepartmentTransferPackTypeCodesByBatchApiView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filter_class = DepartmentTransferPackTypeCodesByBatchFilterSet
    serializer_class = DepartmentTransferPackTypeCodesByBatchSerializer

    def get_queryset(self):
        queryset = pack_and_serial_info.find_available_serializable_pack()

        return queryset

    def list(self, request, *args, **kwargs):
        purchase_detail = self.request.query_params.get('purchase_detail', None)

        if not purchase_detail:
            raise ValidationError({
                "purchase_detail": "Missing query parameters "
            })
        try:
            purchase = PurchaseDetail.objects.get(id=purchase_detail)
        except PurchaseDetail.DoesNotExist:
            return Response({'purchase_detail': 'does not exist'})
        if purchase.item.is_serializable is True:
            qs = pack_and_serial_info.find_available_serializable_pack()
        else:
            qs = pack_and_serial_info.find_available_unserializable_pack()

        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class DepartmentTransferPackTypeDetailCodeByBatchRetrieveApiView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['pack_type_code', 'code']
    serializer_class = DepartmentTransferPackTypeDetailListSerializer

    def get_queryset(self):
        queryset = pack_and_serial_info.find_available_serial_nos()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
