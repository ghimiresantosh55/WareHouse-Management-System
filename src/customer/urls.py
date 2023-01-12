from django.urls import include, path
from rest_framework import routers

from .listing_apis.listing_views import CountryListApiView, SupplierListAPIView
from .views import CustomerViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("customer", CustomerViewSet)

urlpatterns = [
                  path("country-list", CountryListApiView.as_view()),
                  path("supplier-list", SupplierListAPIView.as_view())
              ] + router.urls
