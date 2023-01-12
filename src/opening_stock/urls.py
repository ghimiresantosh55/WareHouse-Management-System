from django.urls import path
from rest_framework.routers import DefaultRouter

from .listing_apis import listing_views
from .views import OpeningStockViewset, SaveOpeningStockView, OpeningStockSummaryViewset
from .views import UpdateLocationPurchaseDetailView

router = DefaultRouter(trailing_slash=False)
router.register('opening-stock', OpeningStockViewset)
router.register('opening-stock-summary', OpeningStockSummaryViewset)
router.register('save-opening-stock', SaveOpeningStockView)
# router.register('update-opening-stock', UpdateOpeningStockViewset)

listing_urls = [
    path("item-list", listing_views.ItemListApiView.as_view()),
    path("packing-type-list", listing_views.PackingTypeListApiView.as_view()),
    path("packing-type-details-list", listing_views.PackingTypeDetailListApiView.as_view()),
]
urlpatterns = [
                  path(
                      "location-purchase-details",
                      UpdateLocationPurchaseDetailView.as_view(),
                      name="update-purchase-detail-location"
                  )
              ] + listing_urls + router.urls
