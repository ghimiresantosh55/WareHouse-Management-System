from django.db import transaction
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from src.purchase.models import PurchaseOrderDetail, PurchaseOrderMaster
from ..purchase_order_serializer.purchase_order_update_serializer import CancelSinglePurchaseOrderSerializer, \
    CancelPurchaseOrderSerializer, UpdatePurchaseOrderSerializer, UpdateDetailPurchaseOrderMasterSerializer, \
    UpdatePurchaseOrderDetailSerializer
from ..serializers import SavePurchaseOrderDocumentsSerializer
from ..purchase_permissions import PurchaseOrderCancelPermission, PurchaseOrderUpdatePermission, PurchaseOrderPermission


class DeleteSinglePurchaseOrderAPIView(UpdateAPIView):
    permission_classes = [PurchaseOrderCancelPermission]
    queryset = PurchaseOrderDetail.objects.all()
    serializer_class = CancelSinglePurchaseOrderSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(DeleteSinglePurchaseOrderAPIView, self).partial_update(request, *args, **kwargs)


class DeletePurchaseOrderAPIView(UpdateAPIView):
    permission_classes = [PurchaseOrderCancelPermission]
    queryset = PurchaseOrderMaster.objects.filter(order_type=1,
                                                  self_purchase_order_master__isnull=True)
    serializer_class = CancelPurchaseOrderSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(DeletePurchaseOrderAPIView, self).partial_update(request, *args, **kwargs)


class AddPurchaseOrderDetailAPIView(UpdateAPIView):
    permission_classes = [PurchaseOrderUpdatePermission]
    queryset = PurchaseOrderMaster.objects.filter(order_type=1,
                                                  self_purchase_order_master__isnull=True)
    serializer_class = UpdatePurchaseOrderSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        # update old purchase_order_details and purchase_order_documents
        all_purchase_order_details = request.data.pop("purchase_order_details")
        all_purchase_order_documents = request.data.pop("purchase_order_documents")

        # save purchase order details
        purchase_order_details_create = []
        for purchase_order_detail in all_purchase_order_details:
            if purchase_order_detail.get("id", False):

                purchase_order_detail_instance = PurchaseOrderDetail.objects.get(id=purchase_order_detail['id'])
                purchase_order_detail_update_serializer = UpdatePurchaseOrderDetailSerializer(
                    purchase_order_detail_instance, data=purchase_order_detail, partial=True
                )
                if purchase_order_detail_update_serializer.is_valid(raise_exception=True):
                    purchase_order_detail_update_serializer.save()
                else:
                    return Response(purchase_order_detail_update_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                purchase_order_details_create.append(purchase_order_detail)

        request.data['purchase_order_details'] = purchase_order_details_create

        # save purchase order documents

        purchase_order_documents_create = []
        for purchase_order_document in all_purchase_order_documents:
            if purchase_order_document.get("id", False):
                purchase_order_document_instance = PurchaseOrderDetail.objects.get(id=purchase_order_document['id'])
                purchase_order_document_update_serializer = SavePurchaseOrderDocumentsSerializer(
                    purchase_order_document_instance, data=purchase_order_document, partial=True
                )
                if purchase_order_document_update_serializer.is_valid(raise_exception=True):
                    purchase_order_document_update_serializer.save()
                else:
                    return Response(purchase_order_document_update_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                purchase_order_documents_create.append(purchase_order_document)

        request.data['purchase_order_documents'] = purchase_order_documents_create
        return super(AddPurchaseOrderDetailAPIView, self).partial_update(request, *args, **kwargs)


class UpdatePurchaseOrderDetailAPIView(UpdateAPIView):
    permission_classes = [PurchaseOrderUpdatePermission]
    queryset = PurchaseOrderMaster.objects.filter(order_type=1, self_purchase_order_master__isnull=True)
    serializer_class = UpdateDetailPurchaseOrderMasterSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(UpdatePurchaseOrderDetailAPIView, self).partial_update(request, *args, **kwargs)
