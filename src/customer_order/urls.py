from django.urls import path
from rest_framework import routers

from .CO_by_batch.views import (
    GetStockByBatchListViewSet, GetPackTypeByBatchRetrieveApiView,
    GetPackTypeDetailByBatchRetrieveApiView, SaveAndVerifyCustomerPackingTypesApiView,
    UpdateCustomerOrderByBatchAPIView)
from .CO_by_batch.views import SaveCustomerOrderByBatchApiView
from .listing_apis import listing_views
from .pickup_views import CustomerOrderPickupViewSet, VerifyCustomerOrderPickupView
from .views import (CancelCustomerOrderViewSet, CancelSingleOrderViewSet, OrderDetailViewSet,
                    OrderMasterViewSet, OrderSummaryViewSet, OrderMasterPickUnverifiedViewSet,
                    OrderMasterPickVerifiedViewSet,
                    SaveOrderView, UpdateCustomerOrderViewSet, ApproveCustomerOrderView)

router = routers.DefaultRouter(trailing_slash=False)

# Check where this URL is used???
router.register("order-master", OrderMasterViewSet, basename="order-masters")
router.register("order-master-pick-unverified", OrderMasterPickUnverifiedViewSet)
router.register("order-master-pick-verified", OrderMasterPickVerifiedViewSet)
router.register("order-detail", OrderDetailViewSet)

listing_urls = [
    path('customer-list', listing_views.CustomerListApiView.as_view()),
    path('discount-scheme-list', listing_views.DiscountSchemeListApiView.as_view()),
    path('item-list', listing_views.ItemListApiView.as_view()),
    path('batch-list', GetStockByBatchListViewSet.as_view()),
    path('pack-type', GetPackTypeByBatchRetrieveApiView.as_view()),
    path('pack-type-detail', GetPackTypeDetailByBatchRetrieveApiView.as_view()),
    path('self-customer-order', listing_views.SelfCustomerOrderListAPIView.as_view()),
]

urlpatterns = [
                  path('save-customer-order', SaveOrderView.as_view(), name='save-customer-order'),
                  path('save-customer-order-by-batch', SaveCustomerOrderByBatchApiView.as_view(),
                       name='save-customer-order-by-batch'),
                  path('order-summary/<int:pk>', OrderSummaryViewSet.as_view(), name='customer-order-summary'),
                  path('cancel-order/<int:pk>', CancelCustomerOrderViewSet.as_view(),
                       name='cancel-complete-customer-order'),
                  path('cancel-single-order/<int:pk>', CancelSingleOrderViewSet.as_view(),
                       name='cancel-single-customer-order'),
                  path('update-customer-order/<int:pk>', UpdateCustomerOrderViewSet.as_view(),
                       name="update-customer-order"),
                  path('update-customer-order-by-batch/<int:pk>', UpdateCustomerOrderByBatchAPIView.as_view(),
                       name="update-customer-order-by-batch"),
                  path('pickup-customer-order', CustomerOrderPickupViewSet.as_view(), name="customer-order-pickup"),
                  path('verify-pickup-customer-order', VerifyCustomerOrderPickupView.as_view(),
                       name="verify-customer-order-pickup"),
                  path('batch-save-pickup-order', SaveAndVerifyCustomerPackingTypesApiView.as_view(),
                       name="batch-save-pickup-order"),
                  path('approve-customer-order/<int:pk>', ApproveCustomerOrderView.as_view(),
                       name="approve-customer-order")
              ] + router.urls + listing_urls
