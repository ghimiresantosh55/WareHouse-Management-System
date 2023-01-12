from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class ReportMaterializedPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_report_materialized' in user_permissions:
            return True
        
        return False


class UserActivityLogPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_user_activity_log' in user_permissions:
            return True
        
        return False
