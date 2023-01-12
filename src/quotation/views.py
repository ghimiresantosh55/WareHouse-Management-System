from django.db import transaction
from django.utils import timezone
from rest_framework import generics, viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView

from .serializers import (QuotationMasterSerializer, QuotationDetailViewSerializer,
                          CancelQuotationMasterSerializer, QuotationSummaryMasterSerializer, \
                          SaveQuotationSerializer, UpdateQuotationSerializer, CancelSingleQuotationDetailSerializer,
                          UpdateQuotationDetailSerializer)
from .models import QuotationMaster, QuotationDetail
from .quotation_permissions import QuotationMasterPermission, QuotationUpdatePermission, QuotationCancelPermission
from django_filters import DateFilter
from rest_framework.response import Response

from ..item.models import Item, ItemCategory


class RangeFilterForQuotationMaster(django_filters.FilterSet):
    start_date_created_date_ad = DateFilter(
        field_name="created_date_ad__date", lookup_expr='gte')
    end_date_created_date_ad = DateFilter(
        field_name="created_date_ad__date", lookup_expr='lte')

    class Meta:
        model = QuotationMaster
        fields = "__all__"


class QuotationMasterAPIView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [QuotationMasterPermission]
    queryset = QuotationMaster.objects.all()
    serializer_class = QuotationMasterSerializer
    filter_class = RangeFilterForQuotationMaster
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'quotation_no', 'delivery_date-ad', 'created_date_ad']
    search_fields = ['quotation_no', 'customer__first_name']


class QuotationDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuotationDetail.objects.all().select_related("quotation", "item")
    serializer_class = QuotationDetailViewSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    common_filter = '__all__'
    search_filter = ['item', 'quotation', 'cancelled']
    search_fields = search_filter
    ordering_fields = common_filter
    filter_fields = search_filter


class QuotationSummaryViewSet(RetrieveAPIView):
    queryset = QuotationMaster.objects.all().select_related("customer")
    serializer_class = QuotationSummaryMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_filter = "__all__"
    search_fields = search_filter
    ordering_fields = search_filter
    filterset_fields = search_filter


class SaveQuotationView(CreateAPIView):
    permission_classes = [QuotationMasterPermission]
    queryset = QuotationMaster.objects.all()
    serializer_class = SaveQuotationSerializer


class UpdateQuotationViewSet(UpdateAPIView):
    permission_classes = [QuotationUpdatePermission]
    queryset = QuotationMaster.objects.all().select_related('customer').prefetch_related(
        'quotation_details')
    serializer_class = UpdateQuotationSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        quotation_details = request.data['quotation_details']
        for quotation_detail in quotation_details:
            try:
                quotation_detail_id = quotation_detail['id']
                QuotationDetail.objects.filter(pk=quotation_detail_id).update(
                    qty=quotation_detail['qty'],
                )
            except KeyError:
                item = quotation_detail['item']
                quotation_detail_item = Item.objects.get(pk=item)
                item_category = quotation_detail['item_category']
                quotation_detail_item_category = ItemCategory.objects.get(pk=item_category)
                QuotationDetail.objects.create(item=quotation_detail_item,
                                               item_category=quotation_detail_item_category,
                                               qty=quotation_detail['qty'],
                                               remarks=quotation_detail['remarks'],
                                               sale_cost=quotation_detail['sale_cost'],
                                               quotation=instance,
                                               created_by=self.request.user,
                                               created_date_ad=timezone.now(),
                                               cancelled=False)
        if request.data['delivery_date_ad'] == "":
            request.data['delivery_date_ad'] = None
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelSingleQuotationDetailAPIView(UpdateAPIView):
    permission_classes = [QuotationCancelPermission]
    queryset = QuotationDetail.objects.filter(cancelled=False)
    serializer_class = CancelSingleQuotationDetailSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class CancelQuotationMasterAPIView(UpdateAPIView):
    permission_classes = [QuotationCancelPermission]
    queryset = QuotationMaster.objects.filter(cancelled=False)
    serializer_class = CancelQuotationMasterSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
