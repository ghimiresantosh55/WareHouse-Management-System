import re
from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from src.user_group.models import CustomPermission


class DashboardFinancialPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_financial_dashboard' in user_permissions:
            return True
        return False


class DashboardStatisticalPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_statistical_dashboard' in user_permissions:
            return True
        return False


class AllDashBoardPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
            user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                'code_name', flat=True
            )
        except:
            return False
        if request.method in SAFE_METHODS and 'view_dashboard' in user_permissions:
            return True
        return False
