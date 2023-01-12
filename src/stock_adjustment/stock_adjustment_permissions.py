from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class PurchaseStockAdditionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_stock_addition' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_stock_addition' in user_permissions:
            return True
        return False


class PurchaseStockSubtractionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_stock_subtraction' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_stock_subtraction' in user_permissions:
            return True
        return False
