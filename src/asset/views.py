import django_filters
from django.db import transaction
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from simple_history.utils import update_change_reason

from .dispatch_serializers import AssetDispatchListSerializer, AssetDispatchPostSerializer, \
    AssetDispatchDetailListSerializer, AssetDispatchReturnSerializer, AssetMaintenanceListSerializer, \
    AssetTransferListSerializer, PickUpAssetDispatchSerializer
from .listing_apis.listing_serializers import PackTypeDetailCodeListSerializer
from .models import AssetIssue, AssetList, AssetService, Asset, AssetCategory, AssetSubCategory, AssetDispatch, \
    AssetDispatchDetail, AssetMaintenance, AssetTransfer
from .unique_no_generator import generate_asset_re_serial, generate_asset_dispatch_no_serial
from .serializers import (AssetIssueCreateSerializer, AssetIssueListSerializer, AssetIssueReturnSerializer,
                          AssetServiceSerializer, AssetSerializer, GetAssetSerializer, AssetCategorySerializer,
                          AssetAssignSerializer,
                          AssetRfidTagsListSerializer, UpdateAssetListLocationListSerializer,
                          UpdateAssetListLocationCreateSerializer,
                          AssetSubCategorySerializer, AssetDetailListSerializer, AssetInfoListSerializer, \
                          AssetMainSummaryReportSerializer, AssetDetailReportSerializer,
                          AssetReportForDurationSerializer)
from ..item.models import Item
from ..item_serialization.models import PackingTypeDetailCode, RfidTag
from ..item_serialization.services.pack_and_serial_info import find_available_item_serial_nos


class AssetsViewSet(ModelViewSet):
    queryset = Asset.objects.all()
    http_method_names = ['get', 'post', 'head']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ['id', 'available', 'scrapped', 'category', 'sub_category']
    search_fields = ['id']
    ordering_fields = ['id']

    @transaction.atomic
    def create(self, request, **kwargs):
        if request.data['depreciation_method'] == 1:
            try:
                salvage_value = request.data['salvage_value']
            except KeyError:
                return Response('please provide salvage value', status=status.HTTP_400_BAD_REQUEST)

            try:
                end_of_life_in_years = request.data['end_of_life_in_years']
            except KeyError:
                return Response('please provide  end_of_life_in_years', status=status.HTTP_400_BAD_REQUEST)

        if request.data['depreciation_method'] == 2:
            try:
                depreciation_rate = request.data['depreciation_rate']
            except KeyError:
                return Response('please provide depreciation_rate', status=status.HTTP_400_BAD_REQUEST)

            try:
                adjusted_book_value = request.data['adjusted_book_value']
            except KeyError:
                return Response('please provide adjusted_book_value', status=status.HTTP_400_BAD_REQUEST)

        asset_details = request.data['asset_details']

        serializer = AssetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            for asset_detail in asset_details:
                packing_type_detail_code = asset_detail['packing_type_detail_code']
                pack_type_detail_code_data = PackingTypeDetailCode.objects.get(id=packing_type_detail_code)
                pack_type_detail_code_data.is_asset = True
                pack_type_detail_code_data.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        serializer_class = GetAssetSerializer
        if self.request.method == 'POST':
            serializer_class = AssetSerializer
        elif self.request.method == 'GET':
            serializer_class = GetAssetSerializer
        return serializer_class


class AssetIssueCreateListViewSet(ModelViewSet):
    queryset = AssetIssue.objects.all()
    http_method_names = ['get', 'post', 'head']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ['id', 'issue_type', 'asset', 'due_date_ad', 'issued_to']
    ordering_fields = ['id']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            serializer_class = AssetIssueCreateSerializer
        elif self.request.method == 'GET':
            serializer_class = AssetIssueListSerializer
        return serializer_class


class AssetIssueReturnViewSet(CreateAPIView):
    serializer_class = AssetIssueReturnSerializer


class AssetServiceViewSet(ModelViewSet):
    queryset = AssetService.objects.all()
    http_method_names = ['get', 'post', 'head']
    serializer_class = AssetServiceSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ['id', 'service_status', 'asset', 'problem']
    ordering_fields = ['id']


class AssetCategoryViewSet(ModelViewSet):
    queryset = AssetCategory.objects.all()
    http_method_names = ['get', 'post', 'patch', 'head']
    serializer_class = AssetCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ['id', 'name']
    search_fields = ['name']
    ordering_fields = ['id']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. At least one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssetSubCategoryViewSet(ModelViewSet):
    queryset = AssetSubCategory.objects.all()
    http_method_names = ['get', 'post', 'patch', 'head']
    serializer_class = AssetSubCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ['id', 'name', 'asset_category']
    search_fields = ['name']
    ordering_fields = ['id']

    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # for log history. At least one reason must be given if update is made
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PackingTypeCodeListingDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PackingTypeDetailCode.objects.filter(pack_type_code__location__isnull=False)
    serializer_class = PackTypeDetailCodeListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', ]
    filterset_fields = ['code']
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        item_id = self.request.query_params.get('item_id', None)
        code = self.request.query_params.get('code', None)
        if not item_id:
            raise ValidationError({
                "item_id": "Missing query parameters "
            })

        try:
            Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"item_id": "does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if not code:
            page = self.paginate_queryset(find_available_item_serial_nos(item_id))
        else:
            page = self.paginate_queryset(
                find_available_item_serial_nos(item_id).filter(code=code)
            )
        if page is not None:
            return self.get_paginated_response(page)

        return Response(page)


class RfidTagsListAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = RfidTag.objects.all()
    serializer_class = AssetRfidTagsListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'code']
    filterset_fields = ['id', 'code']
    http_method_names = ['get']


class SearchAndOrderingFields:
    search_fields = ['id']
    ordering_fields = ['id', ]


class AssetDetailSupplierFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    supplier_id = django_filters.NumberFilter(
        field_name='packing_type_detail_code__pack_type_code__purchase_detail__purchase__supplier')

    class Meta:
        model = AssetList
        fields = ['created_date_ad', 'created_date_bs', 'created_by', 'asset', 'asset__item',
                  'packing_type_detail_code',
                  'packing_type_detail_code__code', 'supplier_id']


class AssetDetailSupplierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetList.objects.all()
    serializer_class = AssetDetailListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = SearchAndOrderingFields.search_fields
    ordering_fields = SearchAndOrderingFields.ordering_fields
    filterset_class = AssetDetailSupplierFilter


class AssetInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetList.objects.all()
    serializer_class = AssetInfoListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = SearchAndOrderingFields.search_fields
    ordering_fields = SearchAndOrderingFields.ordering_fields
    filterset_class = AssetDetailSupplierFilter

    # def list(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     print(instance, "hello hello")
    # asset_packing_type_detail_code=AssetList.objects.filter(packing_type_detail_code= packing_type_detail_code)
    # print(asset_packing_type_detail_code, "this is")
    # rfid_tag = RfidTag.objects.get(code=request.data['rfid_tag_code'])
    # rfid_tag_id = AssetList.objects.get(packing_type_detail_code=rfid_tag.pack_type_detail_code)

    # return  instance


"""""""******************   Reports   *****************"""""""""""""


class SearchAndOrderingFields:
    search_fields = ['id']
    ordering_fields = ['id', ]


class AssetDetailReportFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    supplier_id = django_filters.NumberFilter(
        field_name='packing_type_detail_code__pack_type_code__purchase_detail__purchase__supplier')

    class Meta:
        model = AssetList
        fields = ['created_date_ad', 'created_date_bs', 'created_by', 'asset', 'asset__category', 'asset__sub_category',
                  'asset__salvage_value', 'asset__item', 'asset__depreciation_method', 'asset__scrapped',
                  'asset__end_of_life_in_years',
                  'asset__adjusted_book_value', 'packing_type_detail_code__code', 'supplier_id']


class AssetReportFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = Asset
        fields = "__all__"


class AssetDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetList.objects.all()
    serializer_class = AssetDetailReportSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = SearchAndOrderingFields.search_fields
    ordering_fields = SearchAndOrderingFields.ordering_fields
    filterset_class = AssetDetailReportFilter


class AssetMainReportSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetMainSummaryReportSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = SearchAndOrderingFields.search_fields
    ordering_fields = SearchAndOrderingFields.ordering_fields
    filterset_class = AssetReportFilter


class AssetAssignAPIView(CreateAPIView):
    queryset = RfidTag.objects.all()
    serializer_class = AssetAssignSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(AssetAssignAPIView, self).create(request, *args, **kwargs)


class UpdateAssetListLocationAPIView(ListCreateAPIView):
    queryset = AssetList.objects.all().prefetch_related(
        Prefetch("rfid_tag_codes", queryset=RfidTag.objects.all())
    ).order_by("id").select_related("packing_type_detail_code").select_related("asset", "location")
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'asset', 'location']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UpdateAssetListLocationListSerializer
        elif self.request.method == "POST":
            return UpdateAssetListLocationCreateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssetTimeDurationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetReportForDurationSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = SearchAndOrderingFields.search_fields
    ordering_fields = SearchAndOrderingFields.ordering_fields
    filterset_class = AssetReportFilter


class AssetDispatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetDispatch.objects.all()
    serializer_class = AssetDispatchListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'dispatch_no']
    filter_fields = ['id', 'dispatch_no', 'dispatch_type', 'dispatch_sub_type',
                     'dispatch_info']
    search_fields = ['dispatch_no']
    http_method_names = ['get']


class DispatchAssetDispatchFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')

    class Meta:
        model = AssetDispatch
        fields = ['id', 'dispatch_no', 'dispatch_type', 'dispatch_sub_type',
                  'dispatch_info', 'date']


class DispatchAssetDispatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetDispatch.objects.filter(dispatch_info=1).prefetch_related("asset_dispatches")
    serializer_class = AssetDispatchListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'dispatch_no']
    filterset_class = DispatchAssetDispatchFilterSet
    search_fields = ['dispatch_no']
    http_method_names = ['get']


class AssetDispatchReturnFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
    asset = django_filters.NumberFilter(field_name='asset_dispatches__asset_detail', distinct=True)

    class Meta:
        model = AssetDispatch
        fields = ['id', 'dispatch_no', 'dispatch_type', 'dispatch_sub_type',
                  'dispatch_info', 'date', 'asset', 'ref_dispatch']


class DispatchAssetReturnViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetDispatch.objects.filter(dispatch_info=2).prefetch_related("asset_dispatches")
    serializer_class = AssetDispatchListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'dispatch_no']
    filterset_class = AssetDispatchReturnFilterSet
    search_fields = ['dispatch_no']
    http_method_names = ['get']


class SaveAssetDispatchAPIView(CreateAPIView):
    queryset = AssetDispatch.objects.all()
    serializer_class = AssetDispatchPostSerializer
    http_method_names = ['post']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(SaveAssetDispatchAPIView, self).create(*args, **kwargs)


class AssetDispatchDetailListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetDispatchDetail.objects.all()
    serializer_class = AssetDispatchDetailListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'asset_dispatch', 'picked']
    ordering_fields = ['id']


class AssetMaintenanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetMaintenance.objects.all()
    serializer_class = AssetMaintenanceListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'asset_dispatch']
    ordering_fields = ['id']


class AssetTransferViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetTransfer.objects.all()
    serializer_class = AssetTransferListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'asset_dispatch']
    ordering_fields = ['id']


class AssetDispatchReturn(CreateAPIView):
    queryset = AssetDispatch.objects.all()
    serializer_class = AssetDispatchReturnSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            asset_dispatches = request.data['asset_dispatches']
        except KeyError:
            return Response({"msg": "Provide asset_dispatches"}, status=status.HTTP_400_BAD_REQUEST)
        request.data['dispatch_no'] = generate_asset_dispatch_no_serial(2)
        request.data['dispatch_info'] = 2
        serializer = AssetDispatchReturnSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PickupAssetDispatchAPIView(CreateAPIView):
    serializer_class = PickUpAssetDispatchSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(PickupAssetDispatchAPIView, self).create(request, *args, **kwargs)