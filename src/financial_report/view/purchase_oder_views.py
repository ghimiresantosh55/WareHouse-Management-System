import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

# from core_app.models import FiscalSessionAD
from src.purchase.models import PurchaseOrderMaster
from ..financial_report_permissions import PurchaseOrderReportPermission
from ..serializer.purchase_order_serializers import PurchaseOrderMasterReceivedAndVerifiedSerializer


class FilterForPurchaseOrderMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_ad', 'supplier',
                  'created_by', 'order_type', 'ref_purchase_order']


class PurchaseOrderReceiveAndVerifySummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderReportPermission]
    queryset = PurchaseOrderMaster.objects.filter(ref_purchase_order__isnull=True)
    serializer_class = PurchaseOrderMasterReceivedAndVerifiedSerializer
    filter_class = FilterForPurchaseOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id']
