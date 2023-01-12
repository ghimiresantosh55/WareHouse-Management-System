from django.urls import path, include
from django.urls.resolvers import URLPattern
from rest_framework.routers import DefaultRouter
# from .views import StockAdditionViewset, StockSubtractionView
from .views import PurchaseMasterAdditionViewSet, PurchaseMasterSubtractionViewSet, SavePurchaseAdditionView, \
    SavePurchaseSubtractionView, StockSubtractionSerialNoRetrieveAPIView
from .listing_apis.listing_views import SupplierListAPIView, ItemListAPIView, PurchaseListAPIView,\
    ItemStockSubtractionListAPIView, BatchNoStockSubtractionListAPIView

router = DefaultRouter(trailing_slash=False)
router.register("stock-addition", PurchaseMasterAdditionViewSet)
router.register("stock-subtraction", PurchaseMasterSubtractionViewSet)
router.register("save-stock-addition", SavePurchaseAdditionView)
router.register("save-stock-subtraction", SavePurchaseSubtractionView)

listing_apis = [
    path('supplier-list', SupplierListAPIView.as_view()),
    path('purchase-no-list', PurchaseListAPIView.as_view()),
    path('item-list', ItemListAPIView.as_view()),
    path('item-stock-subtraction-list', ItemStockSubtractionListAPIView.as_view()),
    path('batch-list', BatchNoStockSubtractionListAPIView.as_view()),
    path('serial-no/<str:serial_no>', StockSubtractionSerialNoRetrieveAPIView.as_view()),
]
urlpatterns = [
                  path('', include(router.urls))

              ] + listing_apis
