from django.urls import path
from rest_framework.routers import DefaultRouter

from .listing_apis.views import AccountGroupListViewSet, AccountListViewSet
from .views import ledger_view, ledger_detail_view, AccountGroupViewSet, AccountViewSet, SaveVoucherView, \
    VoucherSummaryViewSet, VoucherMasterViewSet, AccountLedgerView, AccountGroupTreeView, ProfitAndLossReportView, \
    BalanceSheetViewView

router = DefaultRouter(trailing_slash=False)
router.register("account-group", AccountGroupViewSet)
router.register("account", AccountViewSet)

listing_urls = [
    path("account-groups-list", AccountGroupListViewSet.as_view()),
    path("account-list", AccountListViewSet.as_view())
]
urlpatterns = [
                  path('ledger', ledger_view, name='ledger'),
                  path('ledger/<int:account_id>', ledger_detail_view, name='ledger_detail'),
                  path('save-voucher', SaveVoucherView.as_view(), name='save-boucher'),
                  path('voucher-master', VoucherMasterViewSet.as_view(), name='save-boucher'),
                  path('voucher-summary/<int:pk>', VoucherSummaryViewSet.as_view(), name='save-boucher'),
                  path('account-ledger', AccountLedgerView.as_view(), name='account-ledger'),
                  path('account-group-tree', AccountGroupTreeView.as_view(), name='account-ledger'),
                  path('profit-loss-report', ProfitAndLossReportView.as_view(), name='account-ledger'),
                  path('balance-sheet-report', BalanceSheetViewView.as_view(), name='account-ledger'),
              ] + listing_urls + router.urls
