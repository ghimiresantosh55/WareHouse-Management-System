from django.urls import path

from .chalan_stock_views import ChalanStockDetailApiView
from .chalan_to_sale.views import SummaryChalanSaleMasterApiView
from .listing_apis.listing_views import CustomerListApiView, ChalanNoListAPIView
from .views import (CreateChalanApiView, ListChalanMasterChalanApiView,
                    ListChalanMasterReturnedApiView,
                    ListChalanDetailApiView, SummaryChalanMasterApiView, ChalanReturnDropView,
                    ChalanReturnInfoDetailApiView)
from .views import ReturnChalanApiView

listing_urls = [
    path('customer-list', CustomerListApiView.as_view(), name='customer-chalan-list'),
    path('chalan-no-list', ChalanNoListAPIView.as_view(), name='chalan-no-list'),
]
urlpatterns = [
                  path('save-chalan', CreateChalanApiView.as_view(), name='save-chalan'),
                  path('return-chalan', ReturnChalanApiView.as_view(), name='return-chalan'),
                  path('chalan-master-chalan', ListChalanMasterChalanApiView.as_view(), name='chalan-masters-chalan'),
                  path('chalan-master-returned', ListChalanMasterReturnedApiView.as_view(),
                       name='chalan-masters-returned'),
                  path('chalan-detail', ListChalanDetailApiView.as_view(), name='chalan-details'),
                  path('chalan-summary/<int:pk>', SummaryChalanMasterApiView.as_view(), name='chalan-summary'),
                  path('chalan-summary-sale/<int:pk>', SummaryChalanSaleMasterApiView.as_view(),
                       name='chalan-summary-sale'),
                  path('chalan-info', ChalanStockDetailApiView.as_view(), name='chalan-info'),
                  path('chalan-return-info', ChalanReturnInfoDetailApiView.as_view(), name='chalan-return-info'),
                  path('chalan-return-drop', ChalanReturnDropView.as_view(), name='chalan-info'),

              ] + listing_urls
