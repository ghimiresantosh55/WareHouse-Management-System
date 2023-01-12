from django.urls import path
from rest_framework import routers

from .views import LocationViewSet, LocationMapView, LocationItemsListView

router = routers.DefaultRouter(trailing_slash=False)
router.register("location", LocationViewSet)

urlpatterns = [
                  # path('location',LocationViewSet.as_view() ),
                  # path('location/<int:pk>', LocationUpdateViewSet.as_view()),
                  path('location-map', LocationMapView.as_view()),
                  path("location-items", LocationItemsListView.as_view())

              ] + router.urls
