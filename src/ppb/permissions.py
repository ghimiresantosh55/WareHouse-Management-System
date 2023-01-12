from rest_framework.permissions import BasePermission, SAFE_METHODS
from src.user_group.models import CustomPermission


class PPBPermission(BasePermission):
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
        except Exception:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_ppb' in \
                user_permissions:
            return True
        if request.method == 'PATCH' and 'update_ppb' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_ppb' in user_permissions:
            return True
        return False


class TaskPermission(BasePermission):
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
        except Exception:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_task' in \
                user_permissions:
            return True
        if request.method == 'PATCH' and 'update_task' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_task' in user_permissions:
            return True
        return False
