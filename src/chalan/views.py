import django_filters
from django.db import transaction
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView

from src.item_serialization.models import SalePackingTypeCode
from .chalan_permissions import ChalanPermission, ChalanReturnPermission, ChalanDropPermission
from .chalan_return_serializers import ReturnChalanMasterSerializer, ChalanReturnDropSerializer, \
    ChalanDetailReturnInfoSerializer
from .models import ChalanMaster, ChalanDetail
from .serializers import CreateChalanMasterSerializer, \
    ListChalanMasterSerializer, ChalanMasterSummarySerializer, ListChalanDetailsSerializer, \
    ListChalanMasterReturnedSerializer


# Listing Views for chalan


class ChalanMasterFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    status = django_filters.MultipleChoiceFilter(choices=ChalanMaster.STATUS_TYPE)
    item = django_filters.NumberFilter(field_name='chalan_details__item', distinct=True)

    class Meta:
        model = ChalanMaster
        fields = ['date', 'chalan_no', 'id', 'status', 'customer', 'return_dropped', 'item', 'ref_chalan_master']


class SummaryChalanMasterApiView(RetrieveAPIView):
    queryset = ChalanMaster.objects.all().select_related("customer", "discount_scheme").prefetch_related(
        'chalan_details', 'chalan_details__chalan_packing_types')
    serializer_class = ChalanMasterSummarySerializer


class ListChalanMasterChalanApiView(ListAPIView):
    permission_classes = [ChalanPermission]
    queryset = ChalanMaster.objects.filter(status__in=[1, 2]).select_related("customer", "discount_scheme")
    serializer_class = ListChalanMasterSerializer
    filter_class = ChalanMasterFilterSet
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'chalan_no', 'created_date_ad']
    search_fields = ['chalan_no', 'customer__first_name']


class ListChalanMasterReturnedApiView(ListAPIView):
    permission_classes = [ChalanReturnPermission]
    queryset = ChalanMaster.objects.filter(status=3).select_related("customer", "discount_scheme")
    serializer_class = ListChalanMasterReturnedSerializer
    filter_class = ChalanMasterFilterSet
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'chalan_no', 'created_date_ad']
    search_fields = ['chalan_no', 'customer__first_name']


class ListChalanDetailApiView(ListAPIView):
    queryset = ChalanDetail.objects.all().select_related("chalan_master", "item")
    serializer_class = ListChalanDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['item__name']
    ordering_fields = ['id']
    filter_fields = ['chalan_master', 'item']


# Crete and return views for chalan
class CreateChalanApiView(CreateAPIView):
    permission_classes = [ChalanPermission]
    serializer_class = CreateChalanMasterSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(CreateChalanApiView, self).create(request, *args, **kwargs)


class ReturnChalanApiView(CreateAPIView):
    permission_classes = [ChalanReturnPermission]
    serializer_class = ReturnChalanMasterSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(ReturnChalanApiView, self).create(request, *args, **kwargs)


class ChalanReturnDropView(CreateAPIView):
    permission_classes = [ChalanDropPermission]
    serializer_class = ChalanReturnDropSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(ChalanReturnDropView, self).create(request, *args, **kwargs)


class ChalanReturnInfoDetailApiView(ListAPIView):
    permission_classes = [ChalanDropPermission]
    serializer_class = ChalanDetailReturnInfoSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['item__name']
    ordering_fields = ['id']
    filter_fields = ['chalan_master', 'item']

    def get_queryset(self):
        queryset = ChalanDetail.objects.filter(
            chalan_master__status=3, chalan_master__return_dropped=False
        ).prefetch_related(Prefetch(
            'chalan_packing_types',
            queryset=SalePackingTypeCode.objects.prefetch_related(
                'sale_packing_type_detail_code'
            )
        )
        ).select_related("chalan_master", "item",
                         "item_category")
        return queryset
