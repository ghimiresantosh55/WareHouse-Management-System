from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from src.user_group.models import CustomPermission


# permission for customer order purchase_order_view
class CustomerOrderPermission(BasePermission):
    is_superuser = False
    all_permissions = []

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
            self.all_permissions = user_permissions
        except Exception:
            return False
        # check if view_customer_order is in user_permissions or not. If yes permissions is provided
        if (request.method == 'POST' or request.method in SAFE_METHODS) and any(
                permission in ['add_customer_order', 'self_customer_order'] for permission in user_permissions
        ):
            return True
        if request.method in SAFE_METHODS and any(
                permission in ['view_customer_order', 'self_customer_order'] for permission in user_permissions
        ):
            return True
        return False


# permission for customer_order update
class CustomerOrderUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
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
        # check if view_customer_order is in user_permissions or not. If yes permissions is provided
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'update_customer_order' in user_permissions:
            return True
        return False


# permission for customer_order cancellation
class CustomerOrderCancelPermission(BasePermission):

    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
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
        # check if view_customer_order is in user_permissions or not. If yes permissions is provided
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'cancel_customer_order' in user_permissions:
            return True
        if (request.method == 'PATCH') and 'cancel_customer_order' in user_permissions:
            return True
        return False


# permission for customer_order pickup
class CustomerOrderPickupPermission(BasePermission):

    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
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
        # check if view_customer_order is in user_permissions or not. If yes permissions is provided
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'pickup_customer_order' in user_permissions:
            return True
        return False


# permission for customer_order pickup
class CustomerOrderPickupVerifyPermission(BasePermission):

    def has_permission(self, request, view):
        # if unknown user then permission is denied
        if request.user.is_anonymous:
            return False

        # if user is superuser then permission is allowed.
        if request.user.is_superuser is True:
            return True

        # exception handling
        # first try block is checked if condition does not match error is passed
        try:
            groups = request.user.groups.filter(
                is_active=True).values_list('id', flat=True)
            user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                'code_name', flat=True
            )
        except Exception:
            return False
        # check if view_customer_order is in user_permissions or not. If yes permissions is provided
        if (
                request.method == 'POST' or request.method in SAFE_METHODS) and 'pickup_verify_customer_order' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_picked_customer_order' in user_permissions:
            return True
        return False


class ApproveCustomerOrderPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser is True:
            return True

        try:
            groups = request.user.groups.filter(
                is_active=True).values_list('id', flat=True)
            user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                'code_name', flat=True
            )
        except Exception:
            return False
        if request.method == 'PATCH' and 'approve_customer_order' in user_permissions:
            return True
        return False
