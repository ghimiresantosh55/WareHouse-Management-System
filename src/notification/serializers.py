from rest_framework import serializers

from .models import Notifications, UserNotificationMap


class UserNotificationSerializer(serializers.ModelSerializer):
    msg = serializers.ReadOnlyField(source='notification.msg')
    notification_id = serializers.ReadOnlyField(source='notification.id')
    notification_type = serializers.ReadOnlyField(
        source='notification.notification_type')

    created_date_ad = serializers.ReadOnlyField(
        source='notification.created_date_ad')

    class Meta:
        model = UserNotificationMap
        fields = ['id', 'notification_id',
                  'is_read', 'notification_type',
                  'msg', 'created_date_ad']


class ReadNotificationSerailzier(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Notifications.objects.all(), required=True)
    is_read = serializers.SerializerMethodField()

    def create(self, validated_data):
        notification_id = validated_data['id']
        user = self.context.get('request').user

        notification_map = UserNotificationMap.objects.get(user=user,
                                                           notification=notification_id)
        notification_map.is_read = True
        notification_map.save()
        return validated_data

    def get_is_read(self, instance):
        return True
