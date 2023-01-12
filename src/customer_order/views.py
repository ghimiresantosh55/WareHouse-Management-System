import django_filters
from django.db import transaction
from django.db.models import Prefetch
from django_filters import DateFilter
# filter
from django_filters.rest_framework import DjangoFilterBackend
# jwt
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response

from .create_customer_order_helper import generate_customer_order
# permissions
from .customer_order_permissions import (CustomerOrderPermission, CustomerOrderUpdatePermission,
                                         CustomerOrderCancelPermission, ApproveCustomerOrderPermission)
from .customer_order_permissions import CustomerOrderPickupVerifyPermission
from .models import OrderDetail, OrderMaster
# from .serializer import OrderMasterSerializer, OrderDetailSerializer, OrderListMasterSerializer
from .serializers import (CancelCustomerOrderSerializer, CancelSingleOrderSerializer, OrderDetailViewSerializer,
                          OrderMasterSerializer, OrderSummaryMasterSerializer,
                          SaveOrderSerializer, UpdateCustomerOrderSerializer, UpdateCustomerOrderDetailSerializer,
                          ApproveCustomerOrderSerializer)
# importing Models needed in below classes
from ..item_serialization.models import SalePackingTypeCode


class RangeFilterForOrderMaster(django_filters.FilterSet):
    start_date_created_date_ad = DateFilter(
        field_name="created_date_ad__date", lookup_expr='gte')
    end_date_created_date_ad = DateFilter(
        field_name="created_date_ad__date", lookup_expr='lte')
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
    item = django_filters.NumberFilter(field_name='order_details__item', distinct=True)
    cancelled = django_filters.BooleanFilter(field_name='order_details__cancelled')

    class Meta:
        model = OrderMaster
        fields = ['id', 'date', 'item', 'start_date_created_date_ad', 'end_date_created_date_ad',
                  'order_no', 'status', 'customer', 'discount_scheme', 'total_discount', 'total_tax',
                  'sub_total', 'total_discountable_amount', 'total_taxable_amount', 'cancelled',
                  'total_non_taxable_amount', 'delivery_date_ad', 'delivery_date_bs', 'delivery_location',
                  'grand_total', 'pick_verified', 'remarks', 'by_batch', 'created_date_ad', 'created_date_bs',
                  'created_by', 'approved', 'approved_by']


class OrderMasterViewSet(viewsets.ReadOnlyModelViewSet):
    all_permissions = []
    is_superuser = False
    permission_classes = CustomerOrderPermission
    serializer_class = OrderMasterSerializer
    filter_class = RangeFilterForOrderMaster
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'order_no', 'delivery_date-ad', 'created_date_ad']
    search_fields = ['order_no', 'customer__first_name']

    def get_queryset(self):
        if self.is_superuser or 'view_customer_order' in self.all_permissions:
            queryset = OrderMaster.objects.select_related("customer", "discount_scheme").prefetch_related(
                Prefetch('order_details', queryset=OrderDetail.objects.filter(cancelled=False))
            )
        else:
            queryset = OrderMaster.objects.filter(created_by=self.request.user).select_related("customer",
                                                                                               "discount_scheme"
                                                                                               ).prefetch_related(
                Prefetch('order_details', queryset=OrderDetail.objects.filter(cancelled=False))
            )
        return queryset

    def get_permissions(self):
        permission = self.permission_classes()
        return permission

    def check_permissions(self, request):
        permission = self.get_permissions()
        if not permission.has_permission(request, self):

            self.permission_denied(
                request,
                message=getattr(permission, 'message', None)
            )
        else:

            self.is_superuser = permission.is_superuser
            self.all_permissions = permission.all_permissions


class OrderMasterPickVerifiedViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderPickupVerifyPermission]
    queryset = OrderMaster.objects.filter(
        pick_verified=True, status=1).select_related("customer", "discount_scheme")
    serializer_class = OrderMasterSerializer
    filter_class = RangeFilterForOrderMaster
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'order_no', 'delivery_date-ad', 'created_date_ad']
    search_fields = ['order_no', 'customer__first_name']


class OrderMasterPickUnverifiedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderMaster.objects.filter(
        pick_verified=False, status=1).select_related("customer", "discount_scheme")
    serializer_class = OrderMasterSerializer
    filter_class = RangeFilterForOrderMaster
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'order_no', 'delivery_date-ad', 'created_date_ad']
    search_fields = ['order_no', 'customer__first_name']


class OrderDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderDetail.objects.all().select_related("order", "item").prefetch_related(
        Prefetch('customer_packing_types',
                 queryset=SalePackingTypeCode.objects.filter(ref_sale_packing_type_code__isnull=True)))
    serializer_class = OrderDetailViewSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    common_filter = '__all__'
    search_filter = ['item', 'order', 'cancelled']
    search_fields = search_filter
    ordering_fields = common_filter
    filter_fields = search_filter


class OrderSummaryViewSet(RetrieveAPIView):
    queryset = OrderMaster.objects.all().select_related("customer", "discount_scheme").prefetch_related(
        'order_details',
        Prefetch('order_details__customer_packing_types', queryset=SalePackingTypeCode.objects.filter(
            ref_sale_packing_type_code__isnull=True)))
    serializer_class = OrderSummaryMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = search_filter
    ordering_fields = common_filter
    filterset_fields = common_filter


class SaveOrderView(CreateAPIView):
    permission_classes = [CustomerOrderPermission]
    queryset = OrderMaster.objects.all()
    serializer_class = SaveOrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            customer_order_details_data = generate_customer_order(
                request.data['order_details'])
            request.data['order_details'] = customer_order_details_data
        except Exception as e:
            raise e

        #  validation for dates
        if request.data['delivery_date_ad'] == "":
            request.data['delivery_date_ad'] = None

        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelCustomerOrderViewSet(UpdateAPIView):
    permission_classes = [CustomerOrderCancelPermission]
    queryset = OrderMaster.objects.filter(status=1)
    serializer_class = CancelCustomerOrderSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class CancelSingleOrderViewSet(UpdateAPIView):
    permission_classes = [CustomerOrderCancelPermission]
    queryset = OrderDetail.objects.approved()
    serializer_class = CancelSingleOrderSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class UpdateCustomerOrderViewSet(UpdateAPIView):
    permission_classes = [CustomerOrderUpdatePermission]
    queryset = OrderMaster.objects.filter(status=1, by_batch=False).select_related('customer',
                                                                                   'discount_scheme').prefetch_related(
        'order_details')
    serializer_class = UpdateCustomerOrderSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        order_details = request.data.pop('order_details')
        order_details_create = []
        for order_detail in order_details:
            if order_detail.get("id", False):
                order_detail_instance = OrderDetail.objects.get(id=order_detail['id'])
                serializer = UpdateCustomerOrderDetailSerializer(
                    order_detail_instance, data=order_detail, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                order_details_create.append(order_detail)
        request.data['order_details'] = order_details_create
        if request.data['order_details']:
            order_details = generate_customer_order(
                request.data['order_details'])
            request.data['order_details'] = order_details
        if request.data['delivery_date_ad'] == "":
            request.data['delivery_date_ad'] = None
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveCustomerOrderView(UpdateAPIView):
    permission_classes = [ApproveCustomerOrderPermission]
    queryset = OrderMaster.objects.all()
    serializer_class = ApproveCustomerOrderSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
