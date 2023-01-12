from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .purchase_unique_id_generator import generate_order_no
from .serializers import SavePurchaseOrderMasterSerializer
from .verify_po_serializer import PurchaseMasterVerifySerializer


class PurchaseOrderVerifyViewSet(CreateAPIView):
    serializer_class = PurchaseMasterVerifySerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            #  save purchase_order_master data
            purchase_master_data = request.data.copy()
            purchase_details_data = purchase_master_data.pop('purchase_details')
            purchase_order_master_data = {
                "order_no": generate_order_no(4),
                "order_type": 4,
                "sub_total": purchase_master_data['sub_total'],
                "discount_scheme": purchase_master_data['discount_scheme'],
                "total_discount": purchase_master_data['total_discount'],
                "discount_rate": purchase_master_data['discount_rate'],
                "total_discountable_amount": purchase_master_data['total_discountable_amount'],
                "total_taxable_amount": purchase_master_data['total_taxable_amount'],
                "total_non_taxable_amount": purchase_master_data['total_non_taxable_amount'],
                "total_tax": purchase_master_data['total_tax'],
                "grand_total": purchase_master_data['grand_total'],
                "supplier": purchase_master_data['supplier'],
                "remarks": purchase_master_data['remarks'],
                "department": purchase_master_data['department'],
                "terms_of_payment": "",
                "shipment_terms": "",
                "end_user_name": "",
                "ref_purchase_order": purchase_master_data['ref_purchase_order'],
                'purchase_order_details': [],
                'purchase_order_documents': []

            }
            for purchase_detail in purchase_details_data:
                purchase_order_detail_data = {
                    'item': purchase_detail['item'],
                    'purchase_cost': purchase_detail['purchase_cost'],
                    'sale_cost': purchase_detail['sale_cost'],
                    'qty': purchase_detail['qty'],
                    'packing_type': purchase_detail['packing_type'],
                    'packing_type_detail': purchase_detail['packing_type_detail'],
                    "pack_qty": purchase_detail['pack_qty'],
                    'taxable': purchase_detail['taxable'],
                    'tax_rate': purchase_detail['tax_rate'],
                    'tax_amount': purchase_detail['tax_amount'],
                    'discountable': purchase_detail['discountable'],
                    'discount_rate': purchase_detail['discount_rate'],
                    'discount_amount': purchase_detail['discount_amount'],
                    'gross_amount': purchase_detail['gross_amount'],
                    'net_amount': purchase_detail['net_amount'],
                    'ref_purchase_order_detail': purchase_detail['ref_purchase_order_detail']
                }
                purchase_order_master_data['purchase_order_details'].append(purchase_order_detail_data)
            purchase_order_master_serializer = SavePurchaseOrderMasterSerializer(data=purchase_order_master_data,
                                                                                 context={'request': request})
            if purchase_order_master_serializer.is_valid(raise_exception=True):
                purchase_order_master_serializer.save()
            else:
                return Response(purchase_order_master_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
