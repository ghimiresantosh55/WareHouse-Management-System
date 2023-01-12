from django.urls import path
from rest_framework import routers
from .views import AuditCreateApiView, AuditReportApiView, ItemAuditViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("save-audit", AuditCreateApiView)
router.register("save-item-audit", ItemAuditViewSet)

urlpatterns = [
    path('audit-report', AuditReportApiView.as_view())
] + router.urls
