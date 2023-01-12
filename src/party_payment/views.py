import django_filters
from django.db import transaction
from django.utils import timezone
from django_filters import DateFromToRangeFilter
from django_filters.filterset import FilterSet
# filter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from src.custom_lib.functions.current_user import get_created_by
from src.purchase.models import PurchaseMaster
from .models import BasicPartyPayment, PartyPayment, PartyPaymentDetail, BasicPartyPaymentDetail
from .party_payment_permissions import PartyPaymentPermission
from .party_payment_serializer import SavePartyPaymentMasterSerializer
# Custom
from .serializers import PartyPaymentMasterSerializer, PartyPaymentDetailSerializer, PurchaseCreditSerializer, \
    BasicPartyPaymentDetailSerializer
from .serializers import SavePartyPaymentSerializer, SaveBasicPartyPaymentSerializer


# for log


# Create your views here.
class RangeFilterForPartyPayment(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PartyPayment
        fields = '__all__'


class PartyPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentPermission]
    queryset = PartyPayment.objects.all()
    serializer_class = PartyPaymentMasterSerializer
    filter_class = RangeFilterForPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = search_filter
    ordering_fields = common_filter
    filterset_fields = common_filter


class PartyPaymentDetailFilterSet(django_filters.FilterSet):
    purchase_master = django_filters.NumberFilter(field_name='party_payment__purchase_master')

    class Meta:
        model = PartyPaymentDetail
        fields = ['id', 'party_payment', 'purchase_master']


class PartyPaymentDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentPermission]
    queryset = PartyPaymentDetail.objects.all()
    serializer_class = PartyPaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = PartyPaymentDetailFilterSet
    ordering_fields = ['party_clearance', 'id']


class PartyPaymentSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentPermission]
    queryset = PartyPayment.objects.all()
    serializer_class = SavePartyPaymentSerializer
    filter_class = RangeFilterForPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)


class FilterForCreditReportPurchaseMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'created_by', 'created_date_ad', 'pay_type', 'supplier']


class GetPartyInvoice(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentPermission]
    queryset = PurchaseMaster.objects.filter(pay_type=2).select_related("discount_scheme", "supplier",
                                                                        "ref_purchase_order")
    serializer_class = PurchaseCreditSerializer
    filter_class = FilterForCreditReportPurchaseMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no']
    ordering_fields = ['purchase_id', 'created_date_ad']


class SavePartyPaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [PartyPaymentPermission]
    queryset = PartyPayment.objects.all().select_related("purchase_master")
    serializer_class = SavePartyPaymentMasterSerializer
    http_method_names = ['post']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(SavePartyPaymentViewSet, self).create(request, *args, **kwargs)


class FilterForBasicPartyPaymentDetail(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = BasicPartyPaymentDetail
        fields = ['amount', ]


class BasicPartyPaymentDetailViewset(viewsets.ModelViewSet):
    queryset = BasicPartyPaymentDetail.objects.all()
    serializer_class = BasicPartyPaymentDetailSerializer
    http_method_names = ['get']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForBasicPartyPaymentDetail
    ordering_fields = ['id', 'amount']
    search_fields = ['amount', ]


class FilterForBasicPartyPayment(FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = BasicPartyPayment
        fields = ['supplier', 'receipt_no']


class SaveBasicPartyPaymentViewset(viewsets.ModelViewSet):
    queryset = BasicPartyPayment.objects.all()
    permission_classes = [PartyPaymentPermission]
    serializer_class = SaveBasicPartyPaymentSerializer
    http_method_names = ['get', 'head', 'post', 'patch']
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForBasicPartyPayment
    ordering_fields = ['id', 'amount']
    search_fields = ['receipt_no', 'supplier__name']

    @transaction.atomic
    def create(self, request):
        # print(request.data)
        basic_party_payment_serializers = SaveBasicPartyPaymentSerializer(data=request.data,
                                                                          context={'request': request})

        if basic_party_payment_serializers.is_valid(raise_exception=True):
            basic_party_payment_serializers.save()
            return Response(basic_party_payment_serializers.data, status=status.HTTP_201_CREATED)
        return Response(basic_party_payment_serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def partial_update(self, request, pk, *args, **kwargs):
        date_now = timezone.now()
        current_user_id = get_created_by({"request": request}).id

        basic_party_payment_instance = BasicPartyPayment.objects.get(id=pk)
        basic_party_payment_details_update_data = list()
        basic_party_payment_details_create_data = list()

        basic_party_payment_details_data = request.data.pop('basic_party_payment_details')
        for basic_party_payment_detail_data in basic_party_payment_details_data:
            if "id" in basic_party_payment_detail_data:
                basic_party_payment_details_update_data.append(basic_party_payment_detail_data)
            else:
                basic_party_payment_details_create_data.append(basic_party_payment_detail_data)

        # print(basic_party_payment_details_update_data,"basic_party_payment_details_update_data")
        for basic_party_payment_detail_update_data in basic_party_payment_details_update_data:
            basic_party_payment_details_instance = BasicPartyPaymentDetail.objects.get(
                id=int(basic_party_payment_detail_update_data['id']))
            basic_party_payment_details_update_serializer = BasicPartyPaymentDetailSerializer(
                basic_party_payment_details_instance, context={"request": request},
                data=basic_party_payment_detail_update_data, partial=True)
            if basic_party_payment_details_update_serializer.is_valid():
                basic_party_payment_details_update_serializer.save()
            else:
                return Response(basic_party_payment_details_update_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        for basic_party_payment_detail_create_data in basic_party_payment_details_create_data:
            basic_party_payment_detail_create_data['basic_party_payment'] = basic_party_payment_instance.id
            basic_party_payment_detail_create_data['created_by'] = current_user_id
            basic_party_payment_detail_create_data['created_date_ad'] = date_now

            basic_party_payment_details_create_serializer = BasicPartyPaymentDetailSerializer(
                data=basic_party_payment_detail_create_data, context={"request": request})
            if basic_party_payment_details_create_serializer.is_valid(raise_exception=True):
                basic_party_payment_details_create_serializer.save()
            else:
                return Response(basic_party_payment_details_create_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        basic_party_payment_serializer = SaveBasicPartyPaymentSerializer(basic_party_payment_instance,
                                                                         data=request.data, partial=True)
        if basic_party_payment_serializer.is_valid(raise_exception=True):
            basic_party_payment_serializer.save()
            return Response(basic_party_payment_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(basic_party_payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
