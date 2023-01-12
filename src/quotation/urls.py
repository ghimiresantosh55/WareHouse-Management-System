from rest_framework import routers
from django.urls import path
from .views import (QuotationMasterAPIView, QuotationDetailViewSet, QuotationSummaryViewSet, SaveQuotationView,
                    UpdateQuotationViewSet, CancelSingleQuotationDetailAPIView,
                    CancelQuotationMasterAPIView)
from .listing_apis.listing_views import CustomerListApiView, ItemListApiView, RemainingItemListAPIVIew

router = routers.DefaultRouter(trailing_slash=False)
router.register('quotation', QuotationMasterAPIView)
router.register('quotation-detail', QuotationDetailViewSet)

listing_urls = [
    path('customer-list', CustomerListApiView.as_view()),
    path('item-list', ItemListApiView.as_view()),
    path('remaining-item-list', RemainingItemListAPIVIew.as_view()),
]

urlpatterns = [
                  path('quotation-summary/<int:pk>', QuotationSummaryViewSet.as_view(),
                       name="quotation-summary"),
                  path('save-quotation', SaveQuotationView.as_view(),
                       name="save-quotation"),
                  path('update-quotation/<int:pk>', UpdateQuotationViewSet.as_view(),
                       name="update-quotation"),
                  path('cancel-quotation-detail/<int:pk>', CancelSingleQuotationDetailAPIView.as_view(),
                       name="cancel-quotation-detail"),
                  path('cancel-quotation-master/<int:pk>', CancelQuotationMasterAPIView.as_view(),
                       name="cancel-quotation-master")

              ] + router.urls + listing_urls
