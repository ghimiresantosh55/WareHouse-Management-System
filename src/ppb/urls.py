from django.urls import path
from rest_framework import routers

from .listing_apis.listing_views import PPBItemListAPIView, PPBItemCategoryListAPIView, PPBItemUnitListAPIView
from .views import PPBMainViewSet, TaskViewSet, CancelTaskMainAPIView, CancelSingleTaskDetailAPIView, \
    ApproveTaskMainAPIView, PickupTaskAPIView, TaskOutputViewSet, DeletePPBDetailAPIView

router = routers.DefaultRouter(trailing_slash=False)
router.register('ppb-main', PPBMainViewSet, basename="ppb-view-set")
router.register('task-main', TaskViewSet, basename="task-view-set")
router.register('task-output', TaskOutputViewSet, basename="task-view-set")

listing_apis = [
    path('item-list', PPBItemListAPIView.as_view()),
    path('item-category-list', PPBItemCategoryListAPIView.as_view()),
    path('unit-list', PPBItemUnitListAPIView.as_view()),
]

urlpatterns = [
                path('cancel-task-main/<int:pk>', CancelTaskMainAPIView.as_view()),
                path('cancel-task-detail/<int:pk>', CancelSingleTaskDetailAPIView.as_view()),
                path('cancel-task-detail/<int:pk>', ApproveTaskMainAPIView.as_view()),
                path('pickup-task', PickupTaskAPIView.as_view()),

                path('ppb-detail/<int:pk>', DeletePPBDetailAPIView.as_view()),

              ] + router.urls + listing_apis
