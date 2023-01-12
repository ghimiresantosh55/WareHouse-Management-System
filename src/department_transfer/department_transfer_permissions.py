from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from src.user_group.models import CustomPermission


class CrateDepartmentTransferPermission(BasePermission):

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
        if (
                request.method == 'POST' or request.method in SAFE_METHODS) and 'add_department_transfer' in user_permissions:
            return True

        else:
            return False


class ApproveDepartmentTransferPermission(BasePermission):

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
        if (
                request.method == 'POST' or request.method in SAFE_METHODS) and 'approve_department_transfer' in user_permissions:
            return True

        else:
            return False


class ReceiveDepartmentTransferPermission(BasePermission):

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
        if (
                request.method == 'POST' or request.method in SAFE_METHODS) and 'receive_department_transfer' in user_permissions:
            return True

        else:
            return False


class UpdateDepartmentTransferPermission(BasePermission):

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
        if (request.method == 'POST' or request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_department_transfer' in user_permissions:
            return True

        else:
            return False


class ViewDepartmentTransferPermission(BasePermission):

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
        if (request.method in SAFE_METHODS) and 'view_department_transfer' in user_permissions:
            return True
        else:
            return False


class PickDepartmentTransferPermission(BasePermission):

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
        if (
                request.method == 'POST' or request.method in SAFE_METHODS) and 'pickup_department_transfer' in user_permissions:
            return True

        else:
            return False
