
from rest_framework.permissions import SAFE_METHODS, BasePermission
from src.user_group.models import CustomPermission

class RepairPermission(BasePermission):
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
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_repair' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_repair' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_repair' in user_permissions:
            return True
        return False



class RepairUserPermission(BasePermission):
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
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_repair_guy' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_repair_guy' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_repair_guy' in user_permissions:
            return True
        return False
