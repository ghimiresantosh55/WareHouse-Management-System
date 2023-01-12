from django.urls import include, path

from tenant.views import TenantMapView

stock_urls = [

]
urlpatterns = [
                  # for history app
                  path('history/', include('log_app.urls')),
                  # for getting branches
                  path('branches', TenantMapView.as_view()),

                  path('user-app/', include('src.user.urls')),
                  path('core-app/', include('src.core_app.urls')),
                  path('item-app/', include('src.item.urls')),
                  path('supplier-app/', include('src.supplier.urls')),
                  path('purchase-app/', include('src.purchase.urls')),
                  path('opening-stock-app/', include('src.opening_stock.urls')),
                  path('stock-adjustment-app/', include('src.stock_adjustment.urls')),
                  path('customer-app/', include('src.customer.urls')),
                  path('financial-report/', include('src.financial_report.urls')),
                  path('sale-app/', include('src.sale.urls')),
                  path('customer-order-app/', include('src.customer_order.urls')),
                  path('advance-deposit-app/', include('src.advance_deposit.urls')),
                  path('credit-management-app/', include('src.credit_management.urls')),
                  path('party-payment-app/', include('src.party_payment.urls')),
                  path('dashboard-app/', include('src.dashboard.urls')),
                  path('group-app/', include('src.user_group.urls')),
                  path('ird-report-app/', include('src.ird_report.urls')),
                  path('warehouse-location-app/', include('src.warehouse_location.urls')),
                  path("asset-app/", include('src.asset.urls')),
                  path("audit-app/", include('src.audit.urls')),
                  path("chalan-app/", include('src.chalan.urls')),
                  path("item-serialization-app/", include('src.item_serialization.urls')),
                  path("stock-analysis-app/", include('src.stock_analysis.urls')),
                  path("account-app/", include('src.account.urls')),

                  path("notification-app/", include('src.notification.urls')),
                  path("quotation-app/", include('src.quotation.urls')),
                  path("transfer-app/", include('src.transfer.urls')),
                  path("repair-app/", include('src.repair.urls')),
                  path("department-app/", include('src.department.urls')),
                  path("department-transfer-app/", include('src.department_transfer.urls')),
                  path("ppb-app/", include('src.ppb.urls')),
              ] + stock_urls
