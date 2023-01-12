from django.urls import path

from .views import ExpiredItemView, \
    ItemLedgerView, StockAnalysisView, GetStockByBatchViewSet, ItemListAPIView, RemainingItemCostListView, \
    ItemRemainingPackingTypeDetails

urlpatterns = [
    path('stock-analysis', StockAnalysisView.as_view()),
    path('item-ledger', ItemLedgerView.as_view()),
    path('expired-item-report', ExpiredItemView.as_view({'get': 'list'})),
    path("stock-by-batch", GetStockByBatchViewSet.as_view(), name="get-stock-by-batch"),
    path("item-list", ItemListAPIView.as_view()),
    path("stock-analysis-amount", RemainingItemCostListView.as_view()),
    path("remaining-pack-type-codes/<int:item_id>", ItemRemainingPackingTypeDetails.as_view())
]
