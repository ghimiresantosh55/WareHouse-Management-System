from django.urls import path
from .consumer import NotificationConsumer
from src.notification.views import notificationlist


urlpatterns = [
    path('user-notification', notificationlist.NotificationList.as_view()),

    path('user-notification/count',
         notificationlist.UserNotificationCount.as_view()),

    path('user-notification/receive',
         notificationlist.ReadNotificationView.as_view()),

    path('user-notification/read-all', notificationlist.MarkAllAsReadNotificationAPIView.as_view())
]

websocket_urlpatterns1 = [
    path('ws/notification', NotificationConsumer.as_asgi()),

]
