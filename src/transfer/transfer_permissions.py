from rest_framework.permissions import BasePermission, SAFE_METHODS

from src.user_group.models import CustomPermission


class TransferPermission(BasePermission):
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
        if 'transfer' in user_permissions:
            return True
        return False


class TransferOrderPermission(BasePermission):
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
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_transfer_order' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_transfer_order' in user_permissions:
            return True
        if (
                request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_transfer_order' in user_permissions:
            return True
        return False


class CancelTransferOrderPermission(BasePermission):
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
        if 'cancel_transfer_order' in user_permissions:
            return True
        return False


class PickupTransferOrderPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser:
            return True
        try:
            groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
            user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                'code_name', flat=True
            )
        except Exception:
            return False

        if 'pickup_transfer_order' in user_permissions:
            return True
        return False
