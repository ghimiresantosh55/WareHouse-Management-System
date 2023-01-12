from rest_framework.permissions import SAFE_METHODS, BasePermission

from src.user_group.models import CustomPermission


class UserRegisterPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser is True:
            return True
        try:
            groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
            permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                'code_name', flat=True
            )
            if request.method == 'POST' and 'add_user' in permissions_list:
                return True
        except:
            return False


class UserUpdatePermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        if request.user.id == obj.id:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        if request.method == 'PATCH' and 'update_user' in permissions_list:
            return True
        return False


class UserChangePasswordPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        if request.user.id == obj.id:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        if request.method == 'PATCH' and 'change_user_password' in permissions_list:
            return True
        elif request.user.id == obj.id:
            return True
        return False


class UserViewPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        if 'view_user' in permissions_list or 'add_user' in permissions_list or 'update_user' in permissions_list:
            return True
        return False


class UserRetrievePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        if request.user.id == obj.id:
            return True
        return False


class UserListPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        groups = request.user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions_list = CustomPermission.objects.filter(customgroup__in=groups).values_list('code_name', flat=True)
        permissions = ['add_user', 'update_user']
        if request.method in SAFE_METHODS and any(perm in permissions for perm in permissions_list):
            return True
        else:
            return False
