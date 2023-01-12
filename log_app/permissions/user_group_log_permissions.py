from rest_framework.permissions import BasePermission, SAFE_METHODS


class GroupHistoryPermission(BasePermission):
   def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_group_history' in user_permissions:
            return True
        return False


class PermissionHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_permission_history' in user_permissions:
            return True
        return False


class PermissionCategoryHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_permission_category_history' in user_permissions:
            return True
        return False
