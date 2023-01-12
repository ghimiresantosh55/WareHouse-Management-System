from django.urls import path
from rest_framework.routers import DefaultRouter

from .listing_views import ReportUserListApiView, ReportSupplierListApiView, ReportCustomerListApiView, \
    ReportSaleListApiView, ReportPurchaseNoListApiView, ReportItemListAPIView
from .view.party_report_views import SupplierAndCustomerReportApiView
from .view.purchase_oder_views import PurchaseOrderReceiveAndVerifySummaryReportViewSet
from .view.total_amount_calculation_views import CustomerOrderTotalAmountCalcView, FixTotalAmountsCustomerOrderApiView
from .views import ChalanMasterReportViewSet, ChalanDetailReportViewSet, ChalanSummaryReportViewSet, \
    SaleCreditReportSummaryViewSet, PartyPaymentSummaryReportViewSet, UserSaleReportViewSet
from .views import CustomerOrderSummaryViewSet, CustomerOrderDetailReportViewSet, CustomerOrderMasterReportViewSet, \
    PartyPaymentReportViewSet, \
    CreditClearanceReportViewSet, SupplierPartyPaymentReportViewSet
from .views import PurchaseMasterReportViewSet, PurchaseDetailReportViewSet, PurchaseSummaryReportViewSet, \
    ItemwisePurchaseReportViewset
from .views import PurchaseOrderMasterReportViewSet, PurchaseOrderSummaryReportViewSet, \
    StockAdjustmentReportViewSet, StockAdjustmentSummaryReportViewSet
from .views import SaleMasterReportViewSet, SaleDetailReportViewSet, SaleSummaryReportViewSet, SaleCreditReportViewSet

router = DefaultRouter(trailing_slash=False)

# ViewSet registration from purchase
router.register("purchase-order", PurchaseOrderMasterReportViewSet)
router.register("purchase-order-summary", PurchaseOrderSummaryReportViewSet)
router.register("purchase-order-receive-verify-summary", PurchaseOrderReceiveAndVerifySummaryReportViewSet)
router.register("purchase", PurchaseMasterReportViewSet)
router.register("itemwise-purchase-report", ItemwisePurchaseReportViewset)
router.register("stock-adjustment", StockAdjustmentReportViewSet)
router.register("stock-adjustment-summary", StockAdjustmentSummaryReportViewSet)
router.register("purchase-detail", PurchaseDetailReportViewSet)
router.register("purchase-summary", PurchaseSummaryReportViewSet)
router.register("sale", SaleMasterReportViewSet)
router.register("sale-detail", SaleDetailReportViewSet)
router.register("sale-summary", SaleSummaryReportViewSet)
router.register("sale-credit", SaleCreditReportViewSet)  # change to credit-sale
router.register("sale-credit-summary", SaleCreditReportSummaryViewSet)  # change to credit-sale
router.register("order-master", CustomerOrderMasterReportViewSet, basename="order-master-report")
router.register("order-detail", CustomerOrderDetailReportViewSet)
router.register("order-summary", CustomerOrderSummaryViewSet)
# router.register("party-payment", BasicPartyPaymentReportViewset)
# router.register("party-payment-detail", BasicPartyPaymentDetailReportViewSet)
# router.register("party-payment-summary", BasicPartyPaymentSummaryReportViewSet)
router.register("party-payment", PartyPaymentReportViewSet)
router.register("party-payment-summary", PartyPaymentSummaryReportViewSet)
# router.register("party-payment-detail", PartyPaymentDetailReportViewSet)
router.register("chalan-master", ChalanMasterReportViewSet)
router.register("chalan-detail", ChalanDetailReportViewSet)
router.register("chalan-master-summary", ChalanSummaryReportViewSet)
router.register("user-sale-report", UserSaleReportViewSet)

total_amount_query_urls = [
    path('total-amount/customer-order', CustomerOrderTotalAmountCalcView.as_view()),
    path('total-amount/fix-customer-order', FixTotalAmountsCustomerOrderApiView.as_view())
]
urlpatterns = [
                  path('user-list', ReportUserListApiView.as_view()),
                  path('item-list', ReportItemListAPIView.as_view()),
                  path('customer-list', ReportCustomerListApiView.as_view()),
                  path('supplier-list', ReportSupplierListApiView.as_view()),
                  path('sale-no-list', ReportSaleListApiView.as_view()),
                  path('purchase-no-list', ReportPurchaseNoListApiView.as_view()),
                  path('customer-credit', CreditClearanceReportViewSet.as_view()),
                  path('supplier-party-payment', SupplierPartyPaymentReportViewSet.as_view()),
                  path('audit-report', SupplierAndCustomerReportApiView.as_view()),

              ] + total_amount_query_urls + router.urls
