from django.urls import path
from rest_framework import routers
from .views import DepartmentModelViewSet
router = routers.DefaultRouter(trailing_slash=False)
router.register("department", DepartmentModelViewSet)

urlpatterns = [

] + router.urls