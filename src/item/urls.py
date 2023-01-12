from django.urls import path
from rest_framework import routers

from .listing_apis.listing_views import (GenericNameListApiView, ItemCategoryListApiView, ItemListApiView,
                                         ManufacturerListApiView, PackingTypeListApiView,
                                         ItemLocationListApiView, UnitListApiView)
from .views import (GenericNameViewSet, ItemCategoryViewSet, ItemViewSet, ManufacturerViewSet,
                    PackingTypeDetailViewSet, PackingTypeViewSet, UnitViewSet)

router = routers.DefaultRouter(trailing_slash=False)
router.register("unit", UnitViewSet)
router.register("manufacturer", ManufacturerViewSet)
router.register("generic-name", GenericNameViewSet)
router.register("item", ItemViewSet)
router.register("item-category", ItemCategoryViewSet)
router.register("packing-type", PackingTypeViewSet)
router.register("packing-type-detail", PackingTypeDetailViewSet)

listing_urls = [
    path('generic-name-list', GenericNameListApiView.as_view()),
    path('item-category-list', ItemCategoryListApiView.as_view()),
    path('manufacturer-list', ManufacturerListApiView.as_view()),
    path('unit-list', UnitListApiView.as_view()),
    path('item-list', ItemListApiView.as_view()),
    path('packing-type-list', PackingTypeListApiView.as_view()),
    path("location-list", ItemLocationListApiView.as_view())
]

urlpatterns = [

              ] + router.urls + listing_urls
