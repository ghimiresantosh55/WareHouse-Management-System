from django.urls import path
from rest_framework import routers

from .listing_apis import listing_views
from .views import GetCreditInvoice, SaveCreditClearanceViewSet, CreditClearanceViewSet, \
    CreditPaymentDetailViewSet, CreditClearanceSummary

router = routers.DefaultRouter(trailing_slash=False)
router.register("credit-clearance", CreditClearanceViewSet)
router.register("credit-clearance-payment-detail", CreditPaymentDetailViewSet)
router.register("credit-clearance-summary", CreditClearanceSummary)
router.register("get-credit-invoice", GetCreditInvoice)
router.register("clear-credit-invoice", SaveCreditClearanceViewSet)

listing_urls = [
    path("customer-list", listing_views.CustomerListView.as_view(), name="customer-list"),
    path("payment-mode-list", listing_views.PaymentModeListView.as_view(), name="payment-mode-list")
]
urlpatterns = [

              ] + listing_urls + router.urls
