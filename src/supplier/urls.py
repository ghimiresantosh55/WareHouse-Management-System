from django.urls import path
from rest_framework import routers

from .listing_apis.listing_views import CountryListApiView, CustomerListAPIView
from .views import SupplierViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("supplier", SupplierViewSet)


urlpatterns = [
    path('country-list', CountryListApiView.as_view()),
    path('customer-list', CustomerListAPIView.as_view())
] + router.urls
