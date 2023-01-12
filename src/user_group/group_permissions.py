from rest_framework.permissions import SAFE_METHODS, BasePermission

from src.user_group.models import CustomPermission


class GroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        if request.method == 'POST' or request.method in SAFE_METHODS and 'add_role' in permissions_list:
            return True
        if request.method in SAFE_METHODS and 'view_role' in permissions_list:
            return True
        if request.method == 'PATCH' and 'update_role' in permissions_list:
            return True

        return False


class PermissionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        if request.method in SAFE_METHODS and 'add_role' in permissions_list:
            return True
        if request.method in SAFE_METHODS and 'update_role' in permissions_list:
            return True
        return False


class PermissionCategoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        if request.method in SAFE_METHODS and 'add_role' in permissions_list:
            return True
        if request.method in SAFE_METHODS and 'update_role' in permissions_list:
            return True
        return False


class GroupListPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        permissions = ['add_role', 'update_role']
        if request.method in SAFE_METHODS and any(perm in permissions for perm in permissions_list):
            return True
        else:
            return False
