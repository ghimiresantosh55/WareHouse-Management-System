from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class AdvanceDepositHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_advanced_deposit_history' in user_permissions:
            return True
        return False

class AdvanceDepositPaymentDetailHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_advance_deposit_payment_detail_history' in user_permissions:
            return True
        return False