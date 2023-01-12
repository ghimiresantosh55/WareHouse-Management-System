from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from src.user_group.models import CustomPermission


class PurchaseOrderReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_purchase_order_report' in user_permissions:
            return True
        return False


class PurchaseReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_purchase_report' in user_permissions:
            return True
        return False


class StockAdjustmentReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_stock_adjustment' in user_permissions:
            return True
        return False


class SaleReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_item_sale_report' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'self_user_item_sale_report' in user_permissions:
            return True
        return False


class CreditClearanceReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_credit_clearance_report' in user_permissions:
            return True
        return False


class CustomerOrderReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_customer_order_report' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'self_view_customer_order_report' in user_permissions:
            return True
        return False


class BasicPartyPaymentReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_basic_party_payment_report' in user_permissions:
            return True
        return False


class BasicPartyPaymentDetailReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_basic_party_payment_detail_report' in user_permissions:
            return True
        return False


class ChalanReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_chalan_report' in user_permissions:
            return True
        return False


class PartyPaymentReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_party_payment_report' in user_permissions:
            return True
        return False


class PartyPaymentDetailReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_party_payment_detail_report' in user_permissions:
            return True
        return False


class CustomerCreditReportPermission(BasePermission):
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
        except:
            return False
        if request.method in SAFE_METHODS and 'view_customer_credit_report' in user_permissions:
            return True
        return False
