from rest_framework.permissions import SAFE_METHODS, BasePermission


class CountryHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_country_history' in user_permissions:
            return True
        return False


class ProvinceHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_province_history' in user_permissions:
            return True
        return False


class DistrictHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_district_history' in user_permissions:
            return True
        return False


class OrganizationRuleHistoryPermission(BasePermission):
   def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_organization_rule_history' in user_permissions:
            return True
        return False


class OrganizationSetupHistoryPermission(BasePermission):
   def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_organization_setup_history' in user_permissions:
            return True
        return False


class BankHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_bank_history' in user_permissions:
            return True
        return False


class BankDepositHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_bank_deposit_history' in user_permissions:
            return True
        return False


class PaymentModeHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_payment_mode_history' in user_permissions:
            return True
        return False


class DiscountSchemeHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_discount_scheme_history' in user_permissions:
            return True
        return False


class AdditionalChargeTypeHistoryPermission(BasePermission):
   def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_additional_charge_type_history' in user_permissions:
            return True
        return False


class AppAccessLogHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.groups.permissions.values_list('code_name', flat=True)
        except:
            return False
        
        if request.method in SAFE_METHODS and 'view_app_access_log_history' in user_permissions:
            return True
        return False
