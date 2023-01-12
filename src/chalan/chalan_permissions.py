from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from src.user_group.models import CustomPermission


class ChalanPermission(BasePermission):
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
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_chalan' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_chalan' in user_permissions:
            return True
        return False


class ChalanReturnPermission(BasePermission):
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
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_chalan_return' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_chalan_return' in user_permissions:
            return True
        return False


class ChalanDropPermission(BasePermission):
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
        if 'view_chalan_return_drop' in user_permissions:
            return True
        return False
