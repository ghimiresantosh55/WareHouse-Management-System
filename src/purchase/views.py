# from custom
from decimal import Decimal

import django_filters
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from src.custom_lib.functions import stock
# imported models
from .models import (PurchaseAdditionalCharge, PurchaseDetail, PurchaseMaster, PurchaseOrderDetail,
                     PurchaseOrderMaster, PurchasePaymentDetail)
from .purchase_order_serializer.purchase_order_list_serializer import PendingPurchaseOrderMasterListSerializer
from .purchase_permissions import (PurchaseOrderPermission, PurchaseReturnPermission, PurchasePermission,
                                   PurchaseOrderApprovePermission, PurchaseOrderVerifyPermission,
                                   PurchaseOrderReceivePermission, PurchaseOrderPendingPermission,
                                   PurchaseOrderCancelPermission)
# custom files
from .purchase_unique_id_generator import generate_order_no, generate_purchase_no
# imported serializer
from .serializers import (GetPurchaseOrderMasterSerializer, PurchaseAdditionalChargeSerializer,
                          PurchaseDetailSerializer, PurchaseMasterSerializer, PurchaseOrderDetailSerializer,
                          PurchaseOrderMasterSerializer, PurchasePaymentDetailSerializer,
                          SavePurchaseMasterSerializer, SavePurchaseOrderMasterSerializer,
                          PurchaseOrderMasterReceivedSerializer)

'''------------------------------------- get Purchase Order views ---------------------------------------------- '''


# custom filter for bank model
class FilterForGetOrders(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    item = django_filters.NumberFilter(field_name='purchase_order_details__item', distinct=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = ['order_no', 'date', 'created_by__user_name', 'created_date_ad', 'order_type', 'supplier',
                  'currency', 'currency_exchange_rate', 'item', 'ref_purchase_order']


class GetUnAppUnCanPurchaseOrderMasterView(viewsets.ModelViewSet):
    queryset = PurchaseOrderMaster.objects.all().select_related("discount_scheme", "supplier", "ref_purchase_order")
    serializer_class = GetPurchaseOrderMasterSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id', 'order_no']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [PurchaseOrderPermission]
        elif self.action == 'pending':
            self.permission_classes = [PurchaseOrderPendingPermission]
        elif self.action == 'cancelled':
            self.permission_classes = [PurchaseOrderCancelPermission]
        elif self.action == 'approved':
            self.permission_classes = [PurchaseOrderApprovePermission]
        elif self.action == 'received':
            self.permission_classes = [PurchaseOrderReceivePermission]
        elif self.action == 'unverified':
            self.permission_classes = [PurchaseOrderVerifyPermission]
        elif self.action == 'verified':
            self.permission_classes = [PurchaseOrderVerifyPermission]
        return super(self.__class__, self).get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(PurchaseOrderMaster.objects.filter(ref_purchase_order__isnull=True))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request, *args, **kwargs):
        id_list = PurchaseOrderMaster.objects.filter(order_type__gt=1).values_list('ref_purchase_order', flat=True)
        queryset = self.filter_queryset(PurchaseOrderMaster.objects.filter(order_type=1).exclude(id__in=id_list))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cancelled(self, request, *args, **kwargs):
        queryset = self.filter_queryset(PurchaseOrderMaster.objects.filter(order_type=2))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request, *args, **kwargs):
        queryset = self.filter_queryset(PurchaseOrderMaster.objects.filter(order_type=3))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unverified(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            PurchaseOrderMaster.objects.filter(order_type=3, purchaseordermaster__isnull=True))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def verified(self, request, *args, **kwargs):
        queryset = self.filter_queryset(PurchaseOrderMaster.objects.filter(order_type=4))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# read only
class PendingPurchaseOrderMasterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderPendingPermission]
    queryset = PurchaseOrderMaster.objects.filter(ref_purchase_order__isnull=True).select_related(
        "supplier", "ref_purchase_order").prefetch_related('purchase_order_documents')
    serializer_class = PendingPurchaseOrderMasterListSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks', 'grand_total']
    ordering_fields = ['id', 'order_no']


class CancelledPurchaseOrderMasterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderCancelPermission]
    queryset = PurchaseOrderMaster.objects.filter(order_type=2).select_related(
        "discount_scheme", "supplier", "ref_purchase_order")
    serializer_class = PurchaseOrderMasterSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id', 'order_no']


class ReceivedPurchaseOrderMasterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderReceivePermission]
    queryset = PurchaseOrderMaster.objects.filter(order_type=3).select_related(
        "discount_scheme", "supplier", "ref_purchase_order")
    serializer_class = PurchaseOrderMasterReceivedSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks' , 'grand_total']
    ordering_fields = ['id', 'order_no']


class VerifiedPurchaseOrderMasterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderVerifyPermission]
    queryset = PurchaseOrderMaster.objects.filter(order_type=4).select_related(
        "discount_scheme", "supplier", "ref_purchase_order")
    serializer_class = PurchaseOrderMasterSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks', 'grand_total']
    ordering_fields = ['id', 'order_no']


class UnVerifiedPurchaseOrderMasterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderVerifyPermission]
    queryset = PurchaseOrderMaster.objects.filter(order_type=3, self_purchase_order_master__isnull=True).select_related(
        "discount_scheme", "supplier", "ref_purchase_order")
    serializer_class = PurchaseOrderMasterSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id', 'order_no']


# readonly
class PurchaseOrderDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseOrderDetail.objects.all().select_related("item", "packing_type", "item_category", "packing_type",
                                                                "packing_type_detail")
    serializer_class = PurchaseOrderDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['item__name', 'item_category__name']
    ordering_fields = ['id']
    filter_fields = ['id', 'item', 'purchase_order', 'ref_purchase_order_detail']


'''---------------------------------------------- Get views for Purchase ------------------------------- '''


# read only
class PurchaseMasterViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchasePermission]
    queryset = PurchaseMaster.objects.all().select_related("discount_scheme", "supplier", "ref_purchase_order")
    serializer_class = PurchaseMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__name']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type']
    filter_fields = ['id', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier']


class PurchaseMasterPurchaseFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
    item = django_filters.NumberFilter(field_name='purchase_details__item', distinct=True)

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'date', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier', 'item']


# readonly for purchase_type = 1 (purchase)
class PurchaseMasterPurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchasePermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=1, purchasemaster__isnull=True).select_related(
        "discount_scheme", "supplier",
        "ref_purchase_order", "ref_purchase")
    serializer_class = PurchaseMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__name', 'grand_total']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type', 'purchase_no']
    filter_class = PurchaseMasterPurchaseFilterSet


# readonly for purchase_type = 2 (returned)
class PurchaseMasterReturnedViewSet(viewsets.ModelViewSet):
    permission_classes = [PurchaseReturnPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=2).select_related("discount_scheme", "supplier",
                                                                             "ref_purchase_order")
    serializer_class = PurchaseMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__name', 'grand_total']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type', 'purchase_no']
    filter_fields = ['id', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier',
                     'ref_purchase']


# read only for purchase detail
class PurchaseDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseDetail.objects.all().select_related("purchase", "item", "item_category", "packing_type",
                                                           "packing_type_detail").prefetch_related(
        'pu_pack_type_codes', 'pu_pack_type_codes__pack_type_detail_codes'
    )
    serializer_class = PurchaseDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name', 'purchase__purchase_no', 'batch_no']
    ordering_fields = ['id']
    filter_fields = ['purchase', 'item', 'item__fixed_asset']


class PurchasePaymentDetailFilter(filters.FilterSet):
    purchase_order_master = filters.NumberFilter(field_name="purchase_master__ref_purchase_order")

    class Meta:
        model = PurchasePaymentDetail
        fields = ['purchase_master', 'id', 'payment_mode', 'purchase_order_master']


# read only viewset for Payment Details
class PurchasePaymentDetailsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PurchasePaymentDetail.objects.all().select_related("purchase_master", "payment_mode")
    serializer_class = PurchasePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['remarks']
    ordering_fields = ['id', 'purchase_master', 'payment_mode', 'amount']
    filterset_class = PurchasePaymentDetailFilter


# read only viewset for Additional Charges
class PurchaseAdditionalChargeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseAdditionalCharge.objects.all().select_related("charge_type", "purchase_master")
    serializer_class = PurchaseAdditionalChargeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['remarks']
    ordering_fields = ['id', 'charge_type', 'purchase_master', 'amount']
    filter_fields = ['purchase_master', 'id', 'charge_type']


'''----------------------- Views to save purchase order and purchase-------------------------------'''


class SavePurchaseOrderView(viewsets.ModelViewSet):
    permission_classes = [PurchaseOrderPermission]
    queryset = PurchaseOrderMaster.objects.all()
    serializer_class = SavePurchaseOrderMasterSerializer
    http_method_names = ['post']

    @transaction.atomic
    def create(self, request, **kwargs):
        # (request.data)
        request.data['order_type'] = 1
        request.data['order_no'] = generate_order_no(1)

        serializer = SavePurchaseOrderMasterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelPurchaseOrderView(viewsets.ModelViewSet):
    permission_classes = [PurchaseOrderCancelPermission]
    queryset = PurchaseOrderMaster.objects.all().select_related("discount_scheme", "supplier", "ref_purchase_order")
    serializer_class = SavePurchaseOrderMasterSerializer
    http_method_names = ['get', 'head', 'post']

    @transaction.atomic
    def create(self, request, **kwargs):

        try:
            ref_id = request.data['ref_purchase_order']
        except KeyError:
            return Response('please provide ref_purchase_order', status=status.HTTP_400_BAD_REQUEST)

        if PurchaseOrderMaster.objects.filter(ref_purchase_order=ref_id).exists():
            return Response('Order already Approved or cancelled', status=status.HTTP_400_BAD_REQUEST)

        purchase_details = request.data['purchase_order_details']
        ref_purchase_details = []
        for purchase_detail in purchase_details:
            try:
                ref_purchase_details.append(purchase_detail['ref_purchase_order_detail'])
            except KeyError:
                return Response('please provide ref_purchase_order_detail', status=status.HTTP_400_BAD_REQUEST)

        # validation for all purchase order details present in cancel purchase order data
        order_details_id = PurchaseOrderDetail.objects.filter(purchase_order=ref_id).values_list('id', flat=True)
        if len(ref_purchase_details) != len(order_details_id):
            return Response({'object_error': 'Number of purchse order details object  you '
                                             'provided {} not match : available {}'.format(ref_purchase_details,
                                                                                           order_details_id)})
        for ref_purchase in ref_purchase_details:
            if ref_purchase not in order_details_id:
                return Response({'not_exist': 'A Purchase order detail not present in cancel order operation, Please'
                                              'provide all details of master being cancelled'})

        request.data['order_no'] = generate_order_no(2)
        request.data['order_type'] = 2
        serializer = SavePurchaseOrderMasterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ApprovePurchaseOrderView(viewsets.ModelViewSet):
    permission_classes = [PurchaseOrderApprovePermission]
    http_method_names = ['get', 'head', 'post']
    serializer_class = SavePurchaseMasterSerializer
    queryset = PurchaseMaster.objects.all().select_related("discount_scheme", "supplier", "ref_purchase_order")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        quantize_places = Decimal(10) ** -2
        # Key validation fro purchase order master
        try:
            purchase_order_master = request.data.pop('purchase_order_master')
        except KeyError:

            return Response('Provide purchase Order Data in purchase_order_master key',
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            ref_purcahse_order_master = purchase_order_master['ref_purchase_order']

        except KeyError:
            return Response('Provide ref_purchase_order in purchase_order_master key ',
                            status=status.HTTP_400_BAD_REQUEST)
        # for purchase_order_detail in purchase_order_master['purchase_order_details']:
        #     try:
        #         purchase_order_detail['ref_purchase_order_detail']
        #     except ValueError:
        #         return Response('Provide ref_purchase_order_detail purchase_order_master key',
        #                         status=status.HTTP_400_BAD_REQUEST)

        # Key validation fro purchase master
        try:
            purchase_master = request.data.pop('purchase_master')
        except KeyError:
            return Response('Provide purchase Data in purchase_master key')
        try:
            purchase_master['ref_purchase_order']
        except KeyError:
            return Response('Provide ref_purchase_order purchase_master key', status=status.HTTP_400_BAD_REQUEST)
        for purchase_detail in purchase_master['purchase_details']:
            # try:
            #     purchase_detail['ref_purchase_order_detail']
            # except KeyError:
            #     return Response('Provide ref_purchase_order_detail purchase_master key',
            #                     status=status.HTTP_400_BAD_REQUEST)
            try:
                if purchase_detail['expiry_date_ad'] == "":
                    purchase_detail['expiry_date_ad'] = None
            except KeyError:
                return Response({"key_error": "provide expiry_date_ad key"},
                                status=status.HTTP_400_BAD_REQUEST)

        """************************************"""
        # validation for date time fields with blank values
        try:
            purchase_master['bill_no']
            if purchase_master['bill_date_ad'] == "":
                purchase_master['bill_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide bill_no and bill_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            purchase_master['chalan_no']
            if purchase_master['due_date_ad'] == "":
                purchase_master['due_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide chalan_no and due_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)

        purchase_order_master_ref_id = purchase_order_master['ref_purchase_order']
        if PurchaseOrderMaster.objects.filter(ref_purchase_order=purchase_order_master_ref_id).exists():
            return Response('Order already Approved or cancelled', status=status.HTTP_400_BAD_REQUEST)

        # get purchase detials from purchase master
        purchase_details = purchase_master['purchase_details'].copy()

        for purchase_detail in purchase_details:
            purchase_detail['free_purchase'] = False
            if "free_qty" in purchase_detail:
                free_purchase = {
                    "item": purchase_detail["item"],
                    "item_category": purchase_detail["item_category"],
                    "purchase_cost": purchase_detail["purchase_cost"],
                    "sale_cost": purchase_detail["sale_cost"],
                    "taxable": purchase_detail["taxable"],
                    "discountable": purchase_detail["discountable"],
                    "tax_rate": 0,
                    "free_purchase": True,
                    "expirable": purchase_detail["expirable"],
                    "discount_rate": Decimal("0.00"),
                    "discount_amount": Decimal("0.00"),
                    "tax_amount": Decimal("0.00"),
                    "gross_amount": (Decimal(str(purchase_detail['purchase_cost'])) * Decimal(
                        str(purchase_detail['free_qty']))).quantize(quantize_places),
                    "net_amount": (Decimal(str(purchase_detail['purchase_cost'])) * Decimal(
                        str(purchase_detail['free_qty']))).quantize(quantize_places),
                    "expiry_date_ad": purchase_detail["expiry_date_ad"],
                    "batch_no": purchase_detail["batch_no"],
                    "qty": purchase_detail["free_qty"],
                    "pack_qty": purchase_detail["free_pack_qty"],
                    "packing_type": purchase_detail["free_packing_type"],
                    "packing_type_detail": purchase_detail["free_packing_type_detail"],

                }
                purchase_master['purchase_details'].append(free_purchase)

        # insert data for  purchase order master
        purchase_order_master['order_no'] = generate_order_no(3)
        purchase_order_master['order_type'] = 3
        purchase_order_serializer = SavePurchaseOrderMasterSerializer(data=purchase_order_master,
                                                                      context={'request': request})

        # insert data for purchase master
        purchase_master['purchase_no'] = generate_purchase_no(1)
        purchase_master['purchase_type'] = 1
        purchase_serializer = SavePurchaseMasterSerializer(data=purchase_master, context={'request': request})
        # saving both fields data
        if purchase_serializer.is_valid(raise_exception=True):
            if purchase_order_serializer.is_valid(raise_exception=True):
                purchase_serializer.save()
                purchase_order_serializer.save()
                return Response(purchase_order_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(purchase_order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirectApprovePurchaseView(viewsets.ModelViewSet):
    permission_classes = [PurchasePermission]
    http_method_names = ['post', 'head', 'get']
    serializer_class = SavePurchaseMasterSerializer
    queryset = PurchaseMaster.objects.all()

    # queryset = FiscalSessionAD.objects.filter(fiscal_session_ad=

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        quantize_places = Decimal(10) ** -2
        # validation for Date fields being empty

        for purchase_detail in request.data['purchase_details']:
            try:
                if purchase_detail['expiry_date_ad'] == "":
                    purchase_detail['expiry_date_ad'] = None
            except KeyError:
                return Response({"key_error": "provide expiry_date_ad key"},
                                status=status.HTTP_400_BAD_REQUEST)

        # validation for date time fields with blank values
        try:
            request.data['bill_no']
            if request.data['bill_date_ad'] == "":
                request.data['bill_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide bill_no and bill_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            request.data['chalan_no']
            if request.data['due_date_ad'] == "":
                request.data['due_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide chalan_no and due_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)

        # save all data to purchase master
        purchase_master = request.data

        # get purchase details from purchase master
        purchase_details = purchase_master['purchase_details'].copy()

        for purchase_detail in purchase_details:
            purchase_detail['free_purchase'] = False
            if "free_qty" in purchase_detail:
                free_purchase = {
                    "item": purchase_detail["item"],
                    "item_category": purchase_detail["item_category"],
                    "purchase_cost": purchase_detail["purchase_cost"],
                    "sale_cost": purchase_detail["sale_cost"],
                    "taxable": purchase_detail["taxable"],
                    "discountable": purchase_detail["discountable"],
                    "tax_rate": 0,
                    "free_purchase": True,
                    "expirable": purchase_detail["expirable"],
                    "discount_rate": Decimal("0.00"),
                    "discount_amount": Decimal("0.00"),
                    "tax_amount": Decimal("0.00"),
                    "gross_amount": (Decimal(str(purchase_detail['purchase_cost'])) * Decimal(
                        str(purchase_detail['free_qty']))).quantize(quantize_places),
                    "net_amount": (Decimal(str(purchase_detail['purchase_cost'])) * Decimal(
                        str(purchase_detail['free_qty']))).quantize(quantize_places),
                    "expiry_date_ad": purchase_detail["expiry_date_ad"],
                    "batch_no": purchase_detail["batch_no"],
                    "qty": purchase_detail["free_qty"],
                    "pack_qty": purchase_detail["free_pack_qty"],
                    "packing_type": purchase_detail["free_packing_type"],
                    "packing_type_detail": purchase_detail["free_packing_type_detail"],

                }
                purchase_master['purchase_details'].append(free_purchase)

        # saving fields data
        request.data['purchase_no'] = generate_purchase_no(1)

        request.data['purchase_type'] = 1
        serializer = SavePurchaseMasterSerializer(data=purchase_master, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ReturnPurchaseView(CreateAPIView):
    permission_classes = [PurchaseReturnPermission]
    serializer_class = SavePurchaseMasterSerializer

    def create(self, request, *args, **kwargs):
        purchase_detail = request.data['purchase_details']
        for detail in purchase_detail:
            ref_purchase_detail = int(detail['ref_purchase_detail'])
            remaining_quantity = stock.get_remaining_qty_of_purchase(ref_purchase_detail)
            qty = Decimal(detail['qty'])
            if remaining_quantity < qty:
                return Response("Invalid return qty for item {} :remaining quantity {}".format(detail['item_name'],
                                                                                               remaining_quantity),
                                status=status.HTTP_403_FORBIDDEN)

            # if request.data['ref_purchase'] is not None:
            #     return_pay_type = request.data['pay_type']
            #     purchased_pay_type = request.data['ref_purchase'].pay_type

            #     print(request.data['ref_purchase'])
            #     print(request.data['pay_type'])

            #     if return_pay_type != purchased_pay_type:
            #         return Response("Invalid pay_type, return_pay_type should be same as purchased_pay_type")

        request.data['purchase_no'] = generate_purchase_no(2)
        request.data['purchase_type'] = 2
        serializer = SavePurchaseMasterSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
