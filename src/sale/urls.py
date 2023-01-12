from django.urls import path
from rest_framework.routers import DefaultRouter

from .direct_sale.views import DirectSaleSerialNoInfoView, SaveDirectSaleApiView, ItemCostApiView
from .listing_apis.listing_views import CustomerListApiView, SaleNoListAPIView, GetPackTypeByCodeApiView, \
    GetPackTypeDetailApiView, DiscountSchemeListApiView
from .views import (ReturnSaleView, SaleAdditionalChargeViewSet, SaleDetailForReturnViewSet, SaleDetailView,
                    SaleMasterReturnView, SaleMasterSaleView, SaleMasterView, SalePaymentDetailView,
                    SalePrintLogViewset, SaveSaleView, SaleReturnDropView, SaleDetailReturnInfoViewSet)

router = DefaultRouter(trailing_slash=False)

# ViewSet registration from purchase
router.register("sale-master", SaleMasterView)
router.register("sale-master-sale", SaleMasterSaleView)
router.register("sale-master-return", SaleMasterReturnView)
router.register("sale-detail", SaleDetailView)
router.register("get-sale-info", SaleDetailForReturnViewSet, basename="get-sale-info")
router.register("get-sale-return-info", SaleDetailReturnInfoViewSet, basename="get-sale-return-info")
# router.register("save-sale-return", ReturnSaleView)
router.register("sale-payment-detail", SalePaymentDetailView)
router.register("sale-additional-charge", SaleAdditionalChargeViewSet)
router.register("sale-print-log", SalePrintLogViewset)

listing_urls = [
    path("customer-list", CustomerListApiView.as_view(), name="sale-customer-list"),
    path("discount-scheme-list", DiscountSchemeListApiView.as_view(), name="discount-scheme-list"),
    path("sale-no-list", SaleNoListAPIView.as_view(), name="sale-no-list"),
    path("pack-type-code", GetPackTypeByCodeApiView.as_view(), name="pack-type-code-list"),
    path("pack-type-detail-code", GetPackTypeDetailApiView.as_view(), name="pack-type-detail-code-list"),
    path("item-info/<int:pk>", ItemCostApiView.as_view(), name="pack-type-detail-code-list"),
]

direct_sale_urls = [
    path('serial-no-info/<str:code>', DirectSaleSerialNoInfoView.as_view())
]

urlpatterns = [
                  # path("non-dispatched-sale", ListDispatchSaleView.as_view(), name=""),
                  # path("dispatch", CreateDispatchViewSet.as_view(), name=""),
                  path("save-sale", SaveSaleView.as_view(), name="save-sale"),
                  path("save-sale-return", ReturnSaleView.as_view(), name="save-sale-return"),
                  path("sale-return-drop", SaleReturnDropView.as_view(), name="save-sale-return"),
                  path("direct-sale", SaveDirectSaleApiView.as_view(), name="save-direct-sale"),

              ] + listing_urls + router.urls + direct_sale_urls
