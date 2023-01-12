from django.urls import path
from rest_framework import routers

from .listing_apis import listing_views
from .views import GetPartyInvoice, SavePartyPaymentViewSet, PartyPaymentViewSet, \
    PartyPaymentDetailViewSet, PartyPaymentSummaryViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("party-payment", PartyPaymentViewSet)
router.register("party-payment-payment-detail", PartyPaymentDetailViewSet)
router.register("party-payment-summary", PartyPaymentSummaryViewSet)
router.register("get-party-invoice", GetPartyInvoice)
router.register("clear-party-invoice", SavePartyPaymentViewSet)

listing_urls = [
    path("supplier-list", listing_views.SupplierListView.as_view(), name="supplier-list"),
    path("payment-mode-list", listing_views.PaymentModeListView.as_view(), name="supplier-list"),

]

urlpatterns = [

              ] + listing_urls + router.urls
