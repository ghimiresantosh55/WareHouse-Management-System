import decimal
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from .models import PurchaseOrderDetail, PurchaseOrderMaster
from .purchase_permissions import PurchaseOrderApprovePermission, PurchaseOrderReceivePermission
from .receive_purchase_order_serializer import (PurchaseOrderDetailReceivedGetSerializer,
                                                ReceivedPurchaseOrderMasterSerializer)
from ..item_serialization.models import PackingTypeCode

decimal.getcontext().rounding = decimal.ROUND_HALF_UP


class ApprovePurchaseOrderViewApp(CreateAPIView):
    permission_classes = [PurchaseOrderApprovePermission]
    queryset = PurchaseOrderMaster.objects.all()
    serializer_class = ReceivedPurchaseOrderMasterSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        quantize_places = Decimal(10) ** -2
        purchase_order_master = PurchaseOrderMaster.objects.get(id=request.data['ref_purchase_order'])
        try:
            supplier_id = purchase_order_master.supplier.id
        except Exception:
            supplier_id = None

        discount_scheme = purchase_order_master.discount_scheme
        discount_scheme_id = None
        if discount_scheme is not None:
            discount_scheme_id = discount_scheme.id

        purchase_order_master_received_data = {
            "purchase_order_details": [],
            "sub_total": "",
            "grand_total": "",
            "supplier": supplier_id,
            "discount_scheme": request.data.get('discount_scheme', discount_scheme_id),
            "ref_purchase_order": request.data['ref_purchase_order'],
            "discount_rate": purchase_order_master.discount_rate,
            "department": purchase_order_master.department.id

        }

        purchase_order_details = request.data['purchase_order_details']

        sub_total = Decimal('0.00')
        grand_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_non_taxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')

        for purchase_order_detail in purchase_order_details:

            try:
                ref_purchase_order_detail = PurchaseOrderDetail.objects.get(
                    id=purchase_order_detail['ref_purchase_order_detail'])
            except ObjectDoesNotExist:
                return Response({"message": "ref_purchase_order_detail cannot be found "},
                                status=status.HTTP_400_BAD_REQUEST)

            # item = Item.objects.get(id=purchase_detail['item'])
            # creating data for purchase_order_detail and purchase_detail
            purchase_order_detail_data = {
                'item': purchase_order_detail['item'],
                'item_category': ref_purchase_order_detail.item_category.id,
                'purchase_cost': ref_purchase_order_detail.purchase_cost,
                'sale_cost': ref_purchase_order_detail.sale_cost,
                'qty': purchase_order_detail['qty'],
                'packing_type': purchase_order_detail['packing_type'],
                'packing_type_detail': purchase_order_detail['packing_type_detail'],
                'taxable': ref_purchase_order_detail.taxable,
                'tax_rate': ref_purchase_order_detail.tax_rate,
                'tax_amount': "",
                'discountable': ref_purchase_order_detail.discountable,
                'discount_rate': ref_purchase_order_detail.discount_rate,
                'discount_amount': "",
                'gross_amount': "",
                'net_amount': "",
                'ref_purchase_order_detail': purchase_order_detail['ref_purchase_order_detail'],
                'po_pack_type_codes': purchase_order_detail['po_pack_type_codes']
            }

            # calculate gross_amount and net_amount and discount amount

            purchase_order_detail_data['gross_amount'] = Decimal(
                str(Decimal(purchase_order_detail_data['qty']) * Decimal(
                    purchase_order_detail_data['purchase_cost']))).quantize(quantize_places)
            prob_taxable_amount = purchase_order_detail_data['gross_amount']
            if purchase_order_detail['discountable'] is True:
                purchase_order_detail_data['discount_amount'] = Decimal(
                    purchase_order_detail_data['gross_amount'] * purchase_order_detail_data[
                        'discount_rate'] / 100).quantize(quantize_places)
                total_discountable_amount += purchase_order_detail_data['gross_amount']
                prob_taxable_amount -= purchase_order_detail_data['discount_amount']
                total_discount += purchase_order_detail_data['discount_amount']

            else:
                purchase_order_detail_data['discount_amount'] = Decimal('0.00')
            if purchase_order_detail['taxable'] is True:
                purchase_order_detail_data['tax_amount'] = Decimal(
                    prob_taxable_amount * purchase_order_detail_data['tax_rate'] / 100).quantize(quantize_places)
                total_tax += purchase_order_detail_data['tax_amount']
                total_taxable_amount += prob_taxable_amount
            else:
                total_non_taxable_amount += prob_taxable_amount
                purchase_order_detail_data['tax_amount'] = Decimal('0.00')
            purchase_order_detail_data['net_amount'] = purchase_order_detail_data['gross_amount'] - \
                                                       purchase_order_detail_data['discount_amount'] + \
                                                       purchase_order_detail_data['tax_amount']

            sub_total += purchase_order_detail_data['gross_amount']
            grand_total += purchase_order_detail_data['net_amount']
            purchase_order_master_received_data['purchase_order_details'].append(purchase_order_detail_data)

        purchase_order_master_received_data['sub_total'] = sub_total
        purchase_order_master_received_data['grand_total'] = grand_total
        purchase_order_master_received_data['total_discount'] = total_discount
        purchase_order_master_received_data['total_discountable_amount'] = total_discountable_amount
        purchase_order_master_received_data['total_taxable_amount'] = total_taxable_amount
        purchase_order_master_received_data['total_non_taxable_amount'] = total_non_taxable_amount
        purchase_order_master_received_data['total_tax'] = total_tax

        purchase_order_serializer = ReceivedPurchaseOrderMasterSerializer(data=purchase_order_master_received_data,
                                                                          context={'request': request})

        if purchase_order_serializer.is_valid(raise_exception=True):
            purchase_order_serializer.save()
            return Response(purchase_order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(purchase_order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailReceivedListView(ListAPIView):
    permission_classes = [PurchaseOrderReceivePermission]
    serializer_class = PurchaseOrderDetailReceivedGetSerializer
    queryset = PurchaseOrderDetail.objects.filter(purchase_order__order_type=3).select_related(

        "item", "packing_type", "item_category", "packing_type"
    ).prefetch_related(
        Prefetch(
            "po_pack_type_codes", queryset=PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True)
        )
    )
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['item__name', 'item_category__name']
    ordering_fields = ['id']
    filter_fields = ['id', 'item', 'purchase_order', 'ref_purchase_order_detail']
