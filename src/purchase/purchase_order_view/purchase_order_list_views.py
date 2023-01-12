from rest_framework.generics import RetrieveAPIView

from ..models import PurchaseOrderMaster
from ..purchase_order_serializer.purchase_order_list_serializer import PendingPurchaseOrderMasterRetrieveSerializer


class PendingPurchaseOrderMasterRetAPIView(RetrieveAPIView):
    queryset = PurchaseOrderMaster.objects.filter(ref_purchase_order__isnull=True).select_related(
        "supplier", 'supplier__country').prefetch_related(
        "purchase_order_details",
        "purchase_order_details__packing_type_detail",
        "purchase_order_details__packing_type_detail__packing_type")
    serializer_class = PendingPurchaseOrderMasterRetrieveSerializer


class UnVerifiedPurchaseOrderMasterRetAPIView(RetrieveAPIView):
    queryset = PurchaseOrderMaster.objects.filter(order_type=3, self_purchase_order_master__isnull=True).select_related(
        "supplier", 'supplier__country').prefetch_related(
        "purchase_order_details",
        "purchase_order_details__packing_type_detail",
        "purchase_order_details__packing_type_detail__packing_type")
    serializer_class = PendingPurchaseOrderMasterRetrieveSerializer
