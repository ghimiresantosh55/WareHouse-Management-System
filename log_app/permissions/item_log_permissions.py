from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

class UnitHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_unit_history' in user_permissions:
            return True
        return False

class PackingTypePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_packing_type_history' in user_permissions:
            return True
        return False
        
class ManufacturerHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_manufacturer_history' in user_permissions:
            return True
        return False

class GenericNameHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_generic_name_history' in user_permissions:
            return True
        return False

class ItemCategoryHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_item_category_history' in user_permissions:
            return True
        return False

class ItemHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_item_history' in user_permissions:
            return True
        return False
