from django.contrib import admin
from .models import Notifications, UserNotificationMap, NotificationGroup

admin.site.register(Notifications)
admin.site.register(UserNotificationMap)
admin.site.register(NotificationGroup)
