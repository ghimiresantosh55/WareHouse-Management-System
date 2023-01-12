from django.db import models
from rest_framework import fields, serializers
from log_app.models import UserAccessLog
from rest_framework import serializers
from src.user.models import User


class UserLoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccessLog
        fields = "__all__"


class UserHistorySerializer(serializers.ModelSerializer):
    history_date_ad = serializers.ReadOnlyField(source='history_date', allow_null=True)
    class Meta:
        model = User.history.model
        exclude = ['history_date']