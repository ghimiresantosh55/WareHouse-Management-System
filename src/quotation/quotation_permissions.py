from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from src.user_group.models import CustomPermission


# permission for customer order purchase_order_view
class QuotationMasterPermission(BasePermission):

    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            self.is_superuser = True
            return True

        # exception handling
        # first try block is checked if condition doesnot match error is passed
        try:
            groups = request.user.groups.filter(
                is_active=True).values_list('id', flat=True)
            user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                'code_name', flat=True
            )
        except Exception:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and any(
                permission in ['add_quotation'] for permission in user_permissions
        ):
            return True
        if request.method in SAFE_METHODS and any(
                permission in ['view_quotation'] for permission in user_permissions
        ):
            return True
        return False


class QuotationUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'update_quotation' in user_permissions:
            return True
        return False


class QuotationCancelPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'cancel_quotation' in user_permissions:
            return True
        return False
