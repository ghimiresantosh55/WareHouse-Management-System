from src.notification.serializers import UserNotificationSerializer, ReadNotificationSerailzier
from src.notification.models import UserNotificationMap
from rest_framework.generics import ListAPIView, CreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from src.notification.custom_filters import CustomOrderFilter
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction


class NotificationList(ListAPIView):
    serializer_class = UserNotificationSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend, CustomOrderFilter)
    search_fields = ['notification__notification_type', 'notification__msg']
    filter_fields = ['is_read', 'notification']
    ordering_fields = ['created_date_ad']

    def get_queryset(self):
        return UserNotificationMap.objects.filter(user=self.request.user).select_related('notification')


class UserNotificationCount(APIView):

    def get(self, request, *args, **kwargs):
        count = UserNotificationMap.objects.filter(is_read=False,
                                                   user=self.request.user).count()

        total_count = UserNotificationMap.objects.filter(
            user=self.request.user).count()
        return Response({"unread_count": count,
                         "total_count": total_count}, status=status.HTTP_200_OK)


class ReadNotificationView(APIView):

    @transaction.atomic
    def post(self, request):
        serializer = ReadNotificationSerailzier(
            data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkAllAsReadNotificationAPIView(APIView):

    def get(self, request, *args, **kwargs):
        notifications = UserNotificationMap.objects.filter(is_read=False,
                                                           user=request.user)
        for notification in notifications:
            notification.is_read = True
            notification.save()

        return Response(status=status.HTTP_200_OK)
