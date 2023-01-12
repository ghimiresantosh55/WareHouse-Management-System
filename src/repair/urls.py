
from django.urls import path
from rest_framework import routers
from .listing_apis.views import SaleMasterListApiView, SaleDetailListApiView, RepairSummaryViewSet


from .views import RepairViewSet, RepairUserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("repair",  RepairViewSet)
router.register("repair-user",  RepairUserViewSet)


urlpatterns = [
    path("sale-list", SaleMasterListApiView.as_view(), name="sale-list"),  
    path("sale-detail-list", SaleDetailListApiView.as_view(), name="sale-detail-list"),
    path('repair-summary/<int:pk>',  RepairSummaryViewSet.as_view(), name='repair-summary'),
] + router.urls
