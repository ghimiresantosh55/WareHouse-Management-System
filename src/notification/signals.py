import uuid
import channels.layers
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from src.customer_order.models import OrderMaster
from src.item.models import Item
from src.notification.custom_function import CheckUserPermission, SendNotifications
from src.purchase.models import PurchaseOrderMaster
from .models import (
    NotificationGroup, Notifications, UserNotificationMap
)

User = get_user_model()


@receiver(signals.post_save, sender=OrderMaster)
def send_order(instance, created, **kwargs):
    layer = channels.layers.get_channel_layer()
    permission_list = [
        'view_customer_order',
    ]
    users = CheckUserPermission(permission_list, instance)
    current_user = instance.created_by
    try:
        group = NotificationGroup.objects.get(user=current_user)
    except:
        try:
            username = slugify(current_user.user_name)
            group_name = f'notifications_{current_user.pk}_{username}'
            group = NotificationGroup.objects.create(user=current_user,
                                                     group_name=group_name)
        except Exception as e:
            return Exception(str(e))
    group_name = group.group_name
    if created:
        msg = "Created"
    else:
        msg = "Updated"
    notify = Notifications.objects.create(
        msg=f"Customer Order '{instance.order_no}' is successfully '{msg}' by '{current_user.user_name}'  ",
        notification_type="customer-order"
    )
    notify.save()
    for user in users:
        UserNotificationMap.objects.create(
            user=user,
            notification=notify
        )
    try:
        user_map = UserNotificationMap.objects.get(user=current_user,
                                                   notification=notify)
        user_id = user_map.id
    except Exception as e:
        user_id = uuid.uuid4()
    try:
        SendNotifications(layer, group_name, notify, user_id)
    except Exception as e:
        raise Exception(str(e))


@receiver(signals.post_save, sender=Item)
def send_item(instance, created, *args, **kwargs):
    layer = channels.layers.get_channel_layer()
    permission_list = [
        'add_item',
        'view_item',
    ]
    users = CheckUserPermission(permission_list, instance)
    current_user = instance.created_by
    try:
        group = NotificationGroup.objects.get(user=current_user)
    except:
        try:
            username = slugify(current_user.user_name)
            group_name = f'notifications_{current_user.pk}_{username}'
            group = NotificationGroup.objects.create(user=current_user,
                                                     group_name=group_name)
        except Exception as e:
            return Exception(str(e))

    group_name = group.group_name
    if created:
        msg = "Created"
    else:
        msg = "Updated"
    notify = Notifications.objects.create(
        msg=f"Item '{instance.name}' :'{instance.code}' is successfully '{msg}' by '{current_user.user_name}' ",
        notification_type="item"
    )
    notify.save()
    for user in users:
        UserNotificationMap.objects.create(
            user=user,
            notification=notify
        )
    try:
        user_map = UserNotificationMap.objects.get(user=current_user,
                                                   notification=notify)
        user_id = user_map.id
    except Exception as e:
        user_id = uuid.uuid4()
    try:
        SendNotifications(layer, group_name, notify, user_id)
    except Exception as e:
        raise Exception(str(e))


@receiver(signals.post_save, sender=settings.AUTH_USER_MODEL)
def send_user_notification(instance, created, *args, **kwargs):
    if created:
        layer = channels.layers.get_channel_layer()
        permission_list = [
            'add_user',
            'view_user'
        ]
        users = CheckUserPermission(permission_list, instance)
        current_user = instance.created_by
        try:
            group = NotificationGroup.objects.get(user=current_user)
        except Exception as e:
            username = slugify(current_user.user_name)
            group_name = f'notifications_{current_user.pk}_{username}'

            group = NotificationGroup.objects.create(user=current_user,
                                                     group_name=group_name)
        group_name = group.group_name
        notify = Notifications.objects.create(
            msg=f"User '{instance.user_name}'  is successfully 'created' by '{current_user.user_name}' ",
            notification_type="user"
        )
        notify.save()
        for user in users:
            UserNotificationMap.objects.create(
                user=user,
                notification=notify
            )
        try:
            user_map = UserNotificationMap.objects.get(user=current_user,
                                                       notification=notify)
            user_id = user_map.id
        except Exception as e:
            user_id = uuid.uuid4()
        try:
            SendNotifications(layer, group_name, notify, user_id)
        except Exception as e:
            raise Exception(str(e))


@receiver(signals.post_save, sender=PurchaseOrderMaster)
def send_puchase_order_notification(instance, created, **kwargs):
    layer = channels.layers.get_channel_layer()
    permission_list = [
        'view_purchase_order_pending',
    ]
    users = CheckUserPermission(permission_list, instance)
    current_user = instance.created_by
    try:
        group = NotificationGroup.objects.get(user=current_user)
    except:
        try:
            username = slugify(current_user.user_name)
            group_name = f'notifications_{current_user.pk}_{username}'
            group = NotificationGroup.objects.create(user=current_user,
                                                     group_name=group_name)
        except Exception as e:
            return Exception(str(e))
    group_name = group.group_name
    if created:
        msg = "Created"
    else:
        msg = "Updated"
    notify = Notifications.objects.create(
        msg=f"Purchase Order '{instance.order_no}' is successfully '{msg}' by '{current_user.user_name}'  ",
        notification_type="purchase-order"
    )
    notify.save()
    for user in users:
        UserNotificationMap.objects.create(
            user=user,
            notification=notify
        )
    try:
        user_map = UserNotificationMap.objects.get(user=current_user,
                                                   notification=notify)
        user_id = user_map.id
    except Exception as e:
        user_id = uuid.uuid4()
    try:
        SendNotifications(layer, group_name, notify, user_id)
    except Exception as e:
        raise Exception(str(e))
