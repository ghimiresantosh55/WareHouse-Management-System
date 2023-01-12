from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notifications(models.Model):

    msg = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=50)
    created_date_ad = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'


class UserNotificationMap(models.Model):

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    notification = models.ForeignKey(
        Notifications, on_delete=models.PROTECT)
    is_read = models.BooleanField(default=False)


class NotificationGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    group_name = models.CharField(max_length=255)

    def __str__(self):
        return self.group_name
