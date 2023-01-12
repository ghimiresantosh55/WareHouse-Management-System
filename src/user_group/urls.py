from django.urls import include, path
from rest_framework import routers

from .listing_apis.listing_views import PermissionCategoryListApiView, PermissionListApiView
from .views import CustomGroupViewSet, CustomPermissionViewSet, PermissionCategoryViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("group", CustomGroupViewSet)
router.register("permission", CustomPermissionViewSet)
router.register("permission-category", PermissionCategoryViewSet)



urlpatterns = [
   path('permission-list', PermissionListApiView.as_view()),
   path('permission-category-list', PermissionCategoryListApiView.as_view())
] + router.urls
