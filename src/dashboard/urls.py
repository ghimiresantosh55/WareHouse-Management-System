from django.urls.conf import path
from rest_framework import routers
from .views import GetPurchaseViewSet, GetSaleViewSet, GetCreditSaleReportViewset, \
    FinancialDashboardViewSet, GetPurchaseCountViewSet, GetSaleCountViewSet, GetActiveItemCountViewSet, \
    GetCreditSaleCountViewSet, StaticalDashboardViewSet, GetCustomerOrderCountViewSet
from .views import TopCustomersListAPIView, TopSuppliersListAPIView, TopItemListAPIView,\
    PurchaseSaleLineCartListAPIView
from .last_current_week_data import LastAndCurrentWeekStaticalDashboardAPIView
from .chart_apis import (
    purchase_chart_view, chalan_chart_view,
    sale_chart_view, credit_chart_view,
    party_payment_chart_view
)

# for pdf and excel
# from .views import MyExcelViewSet,SaleMasterPDFView
#  MyExcelViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register('financial-dashboard', FinancialDashboardViewSet)
router.register('statical-dashboard', StaticalDashboardViewSet)
router.register('purchase-dashboard', GetPurchaseViewSet)
router.register('sale-dashboard', GetSaleViewSet)
router.register('credit-sale-dashboard', GetCreditSaleReportViewset)
router.register('purchase-count', GetPurchaseCountViewSet)
router.register('sale-count', GetSaleCountViewSet)
router.register('credit-sale-count', GetCreditSaleCountViewSet)
router.register('active-item', GetActiveItemCountViewSet)
router.register('customer-order-count', GetCustomerOrderCountViewSet)
# router.register('excel',MyExcelViewSet)s
# router.register('pdf',SaleMasterPDFView)


# box ->  total sales, Total returned, total purchase, total customer order pending

listing_urls = [
    path('top-customer-list', TopCustomersListAPIView.as_view()),
    path('top-supplier-list', TopSuppliersListAPIView.as_view()),
    path('top-item-list', TopItemListAPIView.as_view()),
    path('line-chart', PurchaseSaleLineCartListAPIView.as_view()),
    path('week-dashboard', LastAndCurrentWeekStaticalDashboardAPIView.as_view()),

    path('purchase-chart', purchase_chart_view.PurchaseVsPurchaseReturnListAPIView.as_view()),
    path('sale-chart', sale_chart_view.SalesVsSalesReturnListAPIView.as_view()),
    path('chalan-chart', chalan_chart_view.ChalanVsChalanReturnListAPIView.as_view()),
    path('credit-chart', credit_chart_view.CreditVsCreditClearanceChartAPIView.as_view()),
    path('payment-chart', party_payment_chart_view.PartyPaymentVsPartyPaymentClearanceListAPIView.as_view()),
]
urlpatterns = [
                  # path('pdf',SaleMasterPDFView.as_view(), name='pdf')
              ] + router.urls + listing_urls

