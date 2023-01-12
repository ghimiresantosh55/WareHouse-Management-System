from django.urls import path, include
from django.urls.resolvers import URLPattern
from django.views.generic.base import View
from .views.advance_deposit import AdvancedDepositHistoryViewSet, AdvancedDepositPaymentDetailHistoryViewset
from .views.customer import CustomerHistoryViewset
from .views.item import UnitHistoryViewset, PackingTypeHistoryViewset, ManufacturerHistoryViewset, GenericNameHistoryViewset, ItemCategoryHistoryViewset, ItemHistoryViewset
from .views.core_app import *
from .views.credit_management import CreditClearanceHistoryViewSet,CreditPaymentDetailHistoryViewSet
from .views.customer_order import OrderMasterHistoryViewSet, OrderDetailHistoryViewSet
from .views.party_payment import PartyClearanceHistroyViewset, PartyPaymentDetailHistroyViewset
from .views.purchase import PurchaseOrderMasterHistroyViewset,PurchaseOrderDetailHistoryViewset,\
    PurchaseMasterHistoryViewset,PurchaseDetailHistoryViewset,\
        PurchasePaymentDetailHistoryViewset, PurchaseAdditionalChargeHistoryViewset
from log_app.views.sale import SaleMasterHistoryViewset, SaleDetailHistoryViewset,\
    SalePaymentDetailHistoryViewset, SaleAdditionalChargeHistoryViewset, SalePrintLogHistoryViewset
from log_app.views.supplier import  SupplierHistoryViewset
from log_app.views.user_group import CustomGroupHistoryViewset,CustomPermissionHistoryViewset, PermissionCategoryHistoryViewset
from .views.user import UserHistoryViewset
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
# advance_deposit_app
router.register("advanced-deposit-history", AdvancedDepositHistoryViewSet)
router.register("advanced-deposit-payment-detail-history", AdvancedDepositPaymentDetailHistoryViewset)

# core_app
router.register("country-history",CountryHistoryViewset)
router.register("province-history",ProvinceHistoryViewset)
router.register("district-history",DistrictHistoryViewset)
router.register("organization-rule-history", OrganizationRuleHistoryViewSet)
router.register("organization-setup-history",OrganizationSetupHistoryViewSet)
router.register("bank-history",BankHistoryViewSet)
router.register("bank-deposit-history",BankDepositHistoryViewSet)
router.register("payment-mode-history", PaymentModeHistoryViewSet)
router.register("discount-scheme-history",DiscountSchemeHistoryViewSet)
router.register("additional-charge-type-history",AdditionalChargeTypeHistoryViewSet)
router.register("app-access-log-history",AppAccessLogHistoryViewset)

# credit_management_app
router.register("credit-clearance-history",CreditClearanceHistoryViewSet)
router.register("credit-payment-detail-history",CreditPaymentDetailHistoryViewSet)

# customer_order_app
router.register("order-master-history", OrderMasterHistoryViewSet)
router.register("order-detail-history", OrderDetailHistoryViewSet)

# Customer_app
router.register("customer-history", CustomerHistoryViewset)

# item_app
router.register("unit-history", UnitHistoryViewset)
router.register("packing-type-history", PackingTypeHistoryViewset)
router.register("manufacturer-history", ManufacturerHistoryViewset)
router.register("generic-name-history", GenericNameHistoryViewset)
router.register("item-category-history", ItemCategoryHistoryViewset)
router.register("item-history", ItemHistoryViewset)

# party_paryment_app
router.register("party-clearance-histroy",PartyClearanceHistroyViewset)
router.register("party-payment-detail-histroy",PartyPaymentDetailHistroyViewset)

# purchase_app
router.register("purchase-order-master-histroy",PurchaseOrderMasterHistroyViewset)
router.register("purchase-order-detail-history",PurchaseOrderDetailHistoryViewset)
router.register("purchase-master-history",PurchaseMasterHistoryViewset)
router.register("purchase-detail-history",PurchaseDetailHistoryViewset)
router.register("purchase-payment-detail-history",PurchasePaymentDetailHistoryViewset)
router.register("purchase-additional-charge-history",PurchaseAdditionalChargeHistoryViewset)

# sale_app
router.register("sale-master-history",SaleMasterHistoryViewset)
router.register("sale-detail-history",SaleDetailHistoryViewset)
router.register("sale-payment-detail-history",SalePaymentDetailHistoryViewset)
router.register("sale-addition-charge-history",SaleAdditionalChargeHistoryViewset)
router.register("sale-print-log-history",SalePrintLogHistoryViewset)

# supplier_app
router.register("supplier-history",SupplierHistoryViewset)

# user_group_app 
router.register("custom-group-history", CustomGroupHistoryViewset)
router.register("custom-permission-history", CustomPermissionHistoryViewset)
router.register("permission-category-history", PermissionCategoryHistoryViewset)

# user_app
router.register("user-history",UserHistoryViewset)

urlpatterns = [
    path('', include(router.urls))
    # path('customer-history',CustomerHistoryListView_as.View(), basename="hello" )
]