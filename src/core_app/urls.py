from django.urls import path
from rest_framework import routers

from .listing_apis.listing_views import BankListApiView, CountryListApiView
from .views import (AdditionalChargeTypeViewSet, AppAccessLogViewset, BankDepositViewSet, BankViewSet,
                    CountryViewSet, DiscountSchemeViewSet, DistrictViewset, FiscalSessionADViewSet,
                    FiscalSessionBSViewSet, OrganizationRuleViewSet, OrganizationSetupViewSet,
                    PaymentModeViewSet, ProvinceViewset, StoreViewSet, CurrencyViewSet, PaymentModeAPIListView)
from .views import SetupInfoView

router = routers.DefaultRouter(trailing_slash=False)
router.register("country", CountryViewSet)
router.register("currency", CurrencyViewSet)
router.register("province", ProvinceViewset)
router.register("district", DistrictViewset)
router.register("organization-setup", OrganizationSetupViewSet)
router.register("organization-rule", OrganizationRuleViewSet)
router.register("bank", BankViewSet)
router.register("bank-deposit", BankDepositViewSet)
router.register("payment-mode", PaymentModeViewSet)
router.register("discount-scheme", DiscountSchemeViewSet)
router.register("additional-charge-type", AdditionalChargeTypeViewSet)
router.register("app-access-log", AppAccessLogViewset)
router.register("store", StoreViewSet)
router.register("fiscal-session-ad", FiscalSessionADViewSet)
router.register("fiscal-session-bs", FiscalSessionBSViewSet)

List_urls = [

    path('country-list', CountryListApiView.as_view()),
    path('bank-list', BankListApiView.as_view()),
    path('payment-mode-list', PaymentModeAPIListView.as_view())
]
urlpatterns = [

                  path('setup-info', SetupInfoView.as_view())
              ] + router.urls + List_urls
