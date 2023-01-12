from django.urls import path
from rest_framework.routers import DefaultRouter

from src.stock_analysis.views import PurchaseDetailStockViewSet
from .direct_purchase.views import SaveDirectPurchaseApiView
from .listing_apis import listing_views
from .location_views import UpdateLocationPurchaseOrderDetailView, UpdateLocationDirectPurchaseDetailView, \
    UpdateBulkLocationPurchaseOrderDetailView, UpdateBulkLocationDirectPurchaseDetailView
from .purchase_document_views import PurchaseDocumentTypeViewSet, PurchaseDocumentViewSet
from .purchase_order_view.purchase_order_list_views import PendingPurchaseOrderMasterRetAPIView, \
    UnVerifiedPurchaseOrderMasterRetAPIView
from .purchase_order_view.purchase_order_update_views import DeleteSinglePurchaseOrderAPIView, \
    DeletePurchaseOrderAPIView, UpdatePurchaseOrderDetailAPIView, AddPurchaseOrderDetailAPIView
from .purchase_order_view.update_documents_view import AddPurchaseOrderDocumentsView, AddPurchaseDocumentsView
from .purchase_return_views import ReturnPurchaseView
from .purchase_stock_views import PurchaseDetailAvailableListView
from .receive_purchase_order_view import ApprovePurchaseOrderViewApp, PurchaseOrderDetailReceivedListView
from .verify_po_views import PurchaseOrderVerifyViewSet
from .views import (GetUnAppUnCanPurchaseOrderMasterView,
                    PurchaseAdditionalChargeViewSet, PurchaseDetailViewSet, PurchaseMasterPurchaseViewSet,
                    PurchaseMasterReturnedViewSet, PurchaseMasterViewSet, PurchaseOrderDetailViewSet,
                    PendingPurchaseOrderMasterViewSet, PurchasePaymentDetailsViewSet,
                    SavePurchaseOrderView, CancelledPurchaseOrderMasterViewSet,
                    ReceivedPurchaseOrderMasterViewSet, VerifiedPurchaseOrderMasterViewSet,
                    UnVerifiedPurchaseOrderMasterViewSet)

router = DefaultRouter(trailing_slash=False)

# ViewSet registration from purchase
router.register("pending-purchase-order-master", PendingPurchaseOrderMasterViewSet)
router.register("cancelled-purchase-order-master", CancelledPurchaseOrderMasterViewSet)
router.register("received-purchase-order-master", ReceivedPurchaseOrderMasterViewSet)
router.register("verified-purchase-order-master", VerifiedPurchaseOrderMasterViewSet)
router.register("unverified-purchase-order-master", UnVerifiedPurchaseOrderMasterViewSet)
router.register("purchase-order-detail", PurchaseOrderDetailViewSet)
router.register('get-orders', GetUnAppUnCanPurchaseOrderMasterView)
router.register("save-purchase-order", SavePurchaseOrderView)
# router.register('cancel-purchase-order', CancelPurchaseOrderView)
router.register("purchase-master", PurchaseMasterViewSet)
router.register("purchase-master-purchase", PurchaseMasterPurchaseViewSet)
router.register("purchase-master-returned", PurchaseMasterReturnedViewSet)
router.register("purchase-detail", PurchaseDetailViewSet)
router.register('get-stock-by-purchase', PurchaseDetailStockViewSet)
router.register('purchase-payment-detail', PurchasePaymentDetailsViewSet)
router.register('purchase-additional-charge', PurchaseAdditionalChargeViewSet)
router.register('purchase-document', PurchaseDocumentViewSet)
router.register('purchase-document-type', PurchaseDocumentTypeViewSet)

stock_urls = [

    path('purchase-detail-available', PurchaseDetailAvailableListView.as_view())
]

update_purchase_order_urls = [
    path('cancel-single-purchase-order/<int:pk>', DeleteSinglePurchaseOrderAPIView.as_view()),
    path('cancel-purchase-order/<int:pk>', DeletePurchaseOrderAPIView.as_view()),
    path('update-purchase-order/<int:pk>', AddPurchaseOrderDetailAPIView.as_view()),
    path('update-purchase-order-detail/<int:pk>', UpdatePurchaseOrderDetailAPIView.as_view()),
]

listing_urls = [
    path("country-list", listing_views.CountryListApiView.as_view(), name=""),
    path("currency-list", listing_views.CurrencyListAPIView.as_view(), name=""),
    path("discount-scheme-list", listing_views.DiscountSchemeListApiView.as_view(), name=""),
    path("packing-type-list", listing_views.PackingTypeListApiView.as_view(), name=""),
    path("item-list", listing_views.ItemListApiView.as_view(), name="purchase-item-list"),
    path("supplier-list", listing_views.SupplierListApiView.as_view(), name=""),
    path("packing-type-detail-list", listing_views.PackingTypeDetailListApiView.as_view(), name=""),
    path("purchase-document-type-list", listing_views.PurchaseDocumentTypeListApiView.as_view(), name=""),
    path("payment-mode-list", listing_views.PaymentModeListApiView.as_view(), name=""),
    path("additional-charge-type-list", listing_views.AdditionalChargeListApiView.as_view(), name=""),
    path("pending-purchase-order-summary/<int:pk>", PendingPurchaseOrderMasterRetAPIView.as_view(), name=""),
    path("unverified-purchase-order-summary/<int:pk>", UnVerifiedPurchaseOrderMasterRetAPIView.as_view(), name=""),
    path("purchase-no-list", listing_views.PurchaseNoListApiView.as_view(), name=""),
    path("purchase-order-no-list", listing_views.PurchaseOrderNoListAPIView.as_view(), name=""),
    path("department-list", listing_views.DepartmentListApiView.as_view(), name=""),
]

urlpatterns = [
                  path("location-purchase-order-details", UpdateLocationPurchaseOrderDetailView.as_view(), name=""),
                  path("location-bulk-purchase-order-details", UpdateBulkLocationPurchaseOrderDetailView.as_view(), name=""),
                  path("location-purchase-details", UpdateLocationDirectPurchaseDetailView.as_view(), name=""),
                  path("location-bulk-purchase-details", UpdateBulkLocationDirectPurchaseDetailView.as_view(), name=""),
                  path("receive-purchase-order", ApprovePurchaseOrderViewApp.as_view(), name=""),
                  path("verify-purchase-order", PurchaseOrderVerifyViewSet.as_view(), name=""),
                  path("purchase-return", ReturnPurchaseView.as_view(), name=""),
                  path('purchase-order-detail-received', PurchaseOrderDetailReceivedListView.as_view()),
                  path('add-purchase-order-documents', AddPurchaseOrderDocumentsView.as_view()),
                  path('add-purchase-documents', AddPurchaseDocumentsView.as_view()),

                  path("direct-purchase", SaveDirectPurchaseApiView.as_view(), name="direct-purchase")
              ] + listing_urls + stock_urls + router.urls + update_purchase_order_urls
