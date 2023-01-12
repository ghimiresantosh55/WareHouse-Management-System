from django.urls import path

from src.department_transfer.listing_apis.views import DepartmentTransferItemListView, \
    DepartmentTransferFromDepartmentList, DepartmentTransferToDepartmentList, GetDepartmentStockByBatchListViewSet, \
    PackingTypeListView, PackingTypeDetailListView, DepartmentTransferPackTypeCodesByBatchApiView, \
    DepartmentTransferPackTypeDetailCodeByBatchRetrieveApiView
from src.department_transfer.receive_transfer.views import ReceiveDepartmentTransferMasterView
from src.department_transfer.views import DepartmentTransferCreateApiView, DepartmentTransferMasterListViewSet, \
    DepartmentTransferMasterSummaryViewSet, CancelDepartmentTransferMasterViewSet, \
    CancelDepartmentTransferDetailViewSet, UpdateDepartmentTransferAPIView, DepartmentTransferDetailListViewSet, \
    ApproveTransferMasterViewSet, PickupDepartmentTransferDetailApiView, DepartmentTransferMasterToListViewSet, \
    DepartmentTransferMasterFromListViewSet

listing_urls = [
    path("item-list", DepartmentTransferItemListView.as_view()),
    path("batch-list", GetDepartmentStockByBatchListViewSet.as_view()),
    path("pack-type-code-list", DepartmentTransferPackTypeCodesByBatchApiView.as_view()),
    path("pack-type-detail-code-list", DepartmentTransferPackTypeDetailCodeByBatchRetrieveApiView.as_view()),
    path("department-from-list", DepartmentTransferFromDepartmentList.as_view()),
    path("department-to-list", DepartmentTransferToDepartmentList.as_view()),
    path("packing-type-list", PackingTypeListView.as_view()),
    path("packing-type-detail-list", PackingTypeDetailListView.as_view()),
    path("department-transfer-master", DepartmentTransferMasterListViewSet.as_view()),
    path("department-transfer-master-to", DepartmentTransferMasterToListViewSet.as_view()),
    path("department-transfer-master-from", DepartmentTransferMasterFromListViewSet.as_view()),
    path("department-transfer-detail", DepartmentTransferDetailListViewSet.as_view()),
    path("department-transfer-summary/<int:pk>", DepartmentTransferMasterSummaryViewSet.as_view())
]
urlpatterns = [
                  path("save-department-transfer", DepartmentTransferCreateApiView.as_view()),
                  path("approve-department-transfer", ApproveTransferMasterViewSet.as_view()),
                  path("pickup-department-transfer", PickupDepartmentTransferDetailApiView.as_view()),
                  path("cancel-department-transfer-detail", CancelDepartmentTransferDetailViewSet.as_view()),
                  path("cancel-department-transfer-master", CancelDepartmentTransferMasterViewSet.as_view()),
                  path('update-department-transfer/<int:pk>', UpdateDepartmentTransferAPIView.as_view(),
                       name="update-department-transfer"),
                  path('receive-department-transfer', ReceiveDepartmentTransferMasterView.as_view(),
                       name="receive-department-transfer"),
              ] + listing_urls
