from django.urls import path
from rest_framework import routers

from .listing_apis import listing_views
from .listing_apis.listing_views import AssetItemViewSet
from .views import AssetIssueCreateListViewSet, AssetIssueReturnViewSet, AssetServiceViewSet, AssetsViewSet, \
    AssetCategoryViewSet, AssetSubCategoryViewSet, PackingTypeCodeListingDetailViewSet, AssetDetailReportViewSet, \
    AssetAssignAPIView, RfidTagsListAPIView, UpdateAssetListLocationAPIView, \
    AssetMainReportSummaryViewSet, \
    AssetTimeDurationViewSet, AssetDetailSupplierViewSet, AssetInfoViewSet, AssetDispatchViewSet, \
    AssetDispatchDetailListViewSet, SaveAssetDispatchAPIView, AssetDispatchReturn, DispatchAssetDispatchViewSet, \
    DispatchAssetReturnViewSet, AssetMaintenanceViewSet, AssetTransferViewSet, PickupAssetDispatchAPIView

router = routers.DefaultRouter(trailing_slash=False)
router.register("asset", AssetsViewSet)
router.register("asset-category", AssetCategoryViewSet)
router.register("asset-sub-category", AssetSubCategoryViewSet)
router.register("asset-issue", AssetIssueCreateListViewSet)
router.register("asset-service", AssetServiceViewSet)
router.register("packing-type-detail-code-list", PackingTypeCodeListingDetailViewSet)
router.register("rfid-tags-list", RfidTagsListAPIView)

router.register("asset-detail-report", AssetDetailReportViewSet, basename="asset-report-detail")
router.register("asset-summary-report", AssetMainReportSummaryViewSet, basename="asset-report-summary")
router.register('asset-item-list', AssetItemViewSet)
router.register('asset-date-report', AssetTimeDurationViewSet)
router.register('asset-detail-supplier-list', AssetDetailSupplierViewSet)
router.register('asset-info-list', AssetInfoViewSet)
router.register('asset-dispatch', AssetDispatchViewSet)
router.register('dispatch-asset-dispatch', DispatchAssetDispatchViewSet)
router.register('dispatch-asset-return', DispatchAssetReturnViewSet)
router.register('asset-dispatch-detail', AssetDispatchDetailListViewSet)
router.register('asset-maintenance', AssetMaintenanceViewSet)
router.register('asset-transfer', AssetTransferViewSet)

listing_urls = [
    path("sn-info/<str:serial_no>", listing_views.SerialNoInfoView.as_view())
]

urlpatterns = [
                  path("save-asset-dispatch", SaveAssetDispatchAPIView.as_view(), name=""),
                  path("save-asset-dispatch-return", AssetDispatchReturn.as_view(), name=""),
                  path("asset-issue/return", AssetIssueReturnViewSet.as_view(), name=""),
                  path("asset-assign/<str:serial_no>", AssetAssignAPIView.as_view(), name=""),
                  path("location-asset-list", UpdateAssetListLocationAPIView.as_view(), name=""),
                  path("pickup-asset-dispatch", PickupAssetDispatchAPIView.as_view(), name=""),
              ] + listing_urls + router.urls
