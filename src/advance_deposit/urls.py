from rest_framework import routers

from django.urls import path, include

from .views import SaveAdvancedDepositViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("save-advanced-deposit", SaveAdvancedDepositViewSet)

urlpatterns = [
    path('', include(router.urls))
]
