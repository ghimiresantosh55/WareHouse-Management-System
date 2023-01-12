from django.urls import path, include
from django.db import router
from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter
from .views import MaterialViewReportViewset, UserActivityLogReportViewset

router = DefaultRouter(trailing_slash=False)
router.register('materialized-purchase-order-view-report', MaterialViewReportViewset)
router.register('user-activity-log-report', UserActivityLogReportViewset)
urlpatterns = [

              ] + router.urls
