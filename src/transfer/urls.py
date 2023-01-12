from django.urls import path

from src.customer_order.CO_by_batch.views import GetStockByBatchListViewSet, GetPackTypeByBatchRetrieveApiView, \
    GetPackTypeDetailByBatchRetrieveApiView
from src.customer_order.listing_apis.listing_views import ItemListApiView, TransferBranchListAPIView
from src.transfer.listing_apis.views import TransferItemPackingTypeListApiView
from src.transfer.views import SaveTransferApiView, TransferMasterListViewSet, TransferDetailListViewSet, \
    PickupTransferDetailViewSet, TransferSummaryApiView, TransferToBranchCreateViewSet, CancelTransferDetailView, \
    CancelTransferMasterView, UpdateTransferApiView

listing_urls = [
    path("item-list", ItemListApiView.as_view()),
    path("branch-list", TransferBranchListAPIView.as_view()),
    path("batch-list", GetStockByBatchListViewSet.as_view()),
    path('pack-type', GetPackTypeByBatchRetrieveApiView.as_view()),
    path('pack-type-detail', GetPackTypeDetailByBatchRetrieveApiView.as_view()),
    path('item-packing-type-list', TransferItemPackingTypeListApiView.as_view()),
]
urlpatterns = [
                  path("transfer-order", SaveTransferApiView.as_view()),
                  path("transfer-summary/<int:pk>", TransferSummaryApiView.as_view()),
                  # path("save-transfer-order", SaveTransferOrderApiView.as_view()),
                  path("transfer-master", TransferMasterListViewSet.as_view()),
                  path("transfer-details", TransferDetailListViewSet.as_view()),
                  # path("transfer-order-master", TransferOrderMasterListViewSet.as_view()),
                  # path("transfer-order-details", TransferOrderDetailListViewSet.as_view()),
                  path("pickup-transfer", PickupTransferDetailViewSet.as_view()),
                  path("transfer", TransferToBranchCreateViewSet.as_view()),
                  path("cancel-transfer-master", CancelTransferMasterView.as_view()),
                  path("cancel-transfer-detail", CancelTransferDetailView.as_view()),
                  path("update-transfer/<int:pk>", UpdateTransferApiView.as_view()),

              ] + listing_urls
