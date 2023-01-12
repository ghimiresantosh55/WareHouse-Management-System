from rest_framework.permissions import SAFE_METHODS, BasePermission

from src.user_group.models import CustomPermission


class UpdatePacketLocationPermission(BasePermission):
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
        except Exception:
            return False
        if (
                request.method == 'POST' or request.method in SAFE_METHODS) and 'update_packet_location' in user_permissions:
            return True
        return False


class PacketInfoPermission(BasePermission):
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
        except Exception:
            return False
        if request.method in SAFE_METHODS and 'update_packet_location' in user_permissions or 'view_packet_info' in user_permissions:
            return True

        return False


class RemainingPacketInfoPermission(BasePermission):
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
        except Exception:
            return False
        if request.method in SAFE_METHODS and 'view_remaining_packet_info' in user_permissions:
            return True

        return False
