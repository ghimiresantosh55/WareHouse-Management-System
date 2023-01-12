from rest_framework import serializers

from src.account.models import AccountGroup, Account


class AccountGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = ['id', 'name']


class VoucherAccountListSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source="group.name", allow_null=True)

    class Meta:
        model = Account
        fields = ['id', 'name', 'group_name', 'group']
