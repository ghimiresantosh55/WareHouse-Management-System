from src.user_group.models import CustomPermission
from src.user_group.models import CustomGroup
from django.contrib.auth import get_user_model
from django.db.models import Q
from asgiref.sync import async_to_sync

User = get_user_model()


def CheckUserPermission(permission_list, instance):
    permissions = CustomPermission.objects.filter(
        code_name__in=permission_list)

    user_groups = CustomGroup.objects.filter(permissions__in=permissions)

    users = User.objects.filter(
        Q(groups__in=user_groups) | Q(id=instance.created_by.id)).distinct()

    return users


def SendNotifications(layer, group_name, notify, user_id):
    async_to_sync(layer.group_send)(group_name, {
        'type': 'send.data',
        'data': {
            "notification_type": notify.notification_type,
            "msg": notify.msg,
            "created_date_ad": str(notify.created_date_ad),
            "notification_id": notify.pk,
            "is_read": False,
            "id": str(user_id)
        }
    })
