from decimal import Decimal

from django.db.models import OuterRef, F, Subquery, Window, Sum, CharField
from django.utils import timezone
from rest_framework import serializers

from src.account.models import VoucherMaster, VoucherDetail, AccountGroup, Account
from src.account.unique_no_generator import generate_voucher_no, generate_account_code


class VoucherSummaryDetailSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source='account.name', allow_null=True)

    class Meta:
        model = VoucherDetail
        fields = ['id', 'account', 'account_name', 'dr_amount', 'cr_amount']


class VoucherSummarySerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    voucher_details = VoucherSummaryDetailSerializer(many=True, read_only=True)

    class Meta:
        model = VoucherMaster
        fields = ['id', 'voucher_no', 'amount', 'date', 'narration', 'reference', 'created_date_ad',
                  'created_date_bs', 'account', 'voucher_details']

    def get_account(self, instance):
        return VoucherDetail.objects.filter(voucher_master=instance).first().account.name


class VoucherMasterListSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()

    class Meta:
        model = VoucherMaster
        fields = ['id', 'voucher_no', 'amount', 'date', 'narration', 'reference', 'created_date_ad', 'created_date_bs',
                  'account']

    def get_account(self, instance):
        return VoucherDetail.objects.filter(voucher_master=instance).first().account.name


class SaveVoucherDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherDetail
        exclude = ['voucher_master']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveVoucherMasterSerializer(serializers.ModelSerializer):
    voucher_details = SaveVoucherDetailSerializer(many=True, required=True)

    class Meta:
        model = VoucherMaster
        fields = ['id', 'voucher_no', 'amount', 'date', 'narration', 'reference', 'created_date_ad', 'created_date_bs',
                  'created_by',
                  'voucher_details']
        read_only_fields = ['voucher_no', 'amount', 'created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        created_by = self.context.get('request').user
        date_now = timezone.now()
        voucher_details = validated_data.pop('voucher_details')
        amount = Decimal("0.00")
        for voucher_detail in voucher_details:
            if voucher_detail['dr_amount'] > Decimal("0.00"):
                amount += voucher_detail['dr_amount']

        voucher_master = VoucherMaster.objects.create(
            **validated_data,
            created_by=created_by,
            created_date_ad=date_now,
            voucher_no=generate_voucher_no(),
            amount=amount
        )

        for voucher_detail in voucher_details:
            VoucherDetail.objects.create(
                **voucher_detail,
                created_by=created_by,
                created_date_ad=date_now,
                voucher_master=voucher_master
            )
        return voucher_master

    def validate_voucher_details(self, voucher_details):
        cr_amount = Decimal("0.00")
        cr_count = 0
        dr_count = 0
        dr_amount = Decimal("0.00")
        for voucher in voucher_details:
            if voucher['dr_amount'] > Decimal("0.00"):
                dr_amount += voucher['dr_amount']
                dr_count += 1
            if voucher['cr_amount'] > Decimal("0.00"):
                cr_amount += voucher['cr_amount']
                cr_count += 1

        if cr_amount != dr_amount:
            raise serializers.ValidationError({"amount": "cr_amount != dr_amount"})

        if cr_count == 0 or dr_count == 0:
            raise serializers.ValidationError({"amount": "cr_amount,  dr_amount cannot be zero"})

        if cr_count > 1 and dr_count > 1:
            raise serializers.ValidationError({"amount": "multiple cr or multiple dr are accepted not both"})
        return voucher_details


class AccountGroupParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = ['id', 'name']


class AccountGroupSerializer(serializers.ModelSerializer):
    parent = AccountGroupParentSerializer(read_only=True)

    class Meta:
        model = AccountGroup
        fields = ['id', 'name', 'parent', 'created_date_ad', 'created_date_bs', 'created_by']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class AccountGroupSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = ['id', 'name', 'parent', 'created_date_ad', 'created_date_bs', 'created_by']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        return AccountGroup.objects.create(**validated_data,
                                           created_by=self.context.get('request').user,
                                           created_date_ad=timezone.now()
                                           )

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        instance.save()
        return instance


class NestedAccountGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = ['id', 'name']


class AccountListSerializer(serializers.ModelSerializer):
    group = NestedAccountGroupSerializer(read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'name', 'group', 'created_date_ad', 'created_date_bs', 'created_by']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'group', 'created_date_ad', 'created_date_bs', 'created_by']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        return Account.objects.create(
            **validated_data,
            created_by=self.context.get('request').user,
            created_date_ad=timezone.now(),
            type="ACCOUNT",
            code=generate_account_code("ACCOUNT")
        )

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class AccountLedgerSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source="group.name", allow_null=True)
    ledger = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'code', 'type', 'group', 'opening_balance', 'group_name', 'ledger']

    def get_ledger(self, account):
        request = self.context.get("request")
        query_parameters = request.query_params
        date_after = ""
        date_before = ""
        if 'date_after' in query_parameters:
            date_after = query_parameters['date_after']

        if 'date_before' in query_parameters:
            date_before = query_parameters['date_before']

        ref_account = VoucherDetail.objects.filter(voucher_master=OuterRef('voucher_master')).exclude(
            id=OuterRef('id')).annotate(
            ref_name=F('account__name')).values(
            "ref_name")[:1]

        queryset = VoucherDetail.objects.filter(account=account)
        if date_after:
            queryset = queryset.filter(created_date_ad__date__gte=date_after)
        if date_before:
            queryset = queryset.filter(created_date_ad__date__lte=date_before)

        ledger = queryset.annotate(differ=F('dr_amount') - F('cr_amount'),
                                   ref_account=Subquery(
                                       ref_account,
                                       output_field=CharField()),
                                   type=F('voucher_master__type'),
                                   voucher_no=F('voucher_master__voucher_no'),
                                   narration=F('voucher_master__narration')
                                   ).annotate(
            balance=Window(
                expression=
                Sum('differ'),
                order_by=F('id').asc()
            )
        ).values('id', 'ref_account', 'created_date_ad', 'created_date_bs',
                 'dr_amount', 'cr_amount', 'balance', 'type', 'voucher_no', 'voucher_master', 'narration')
        print(ledger.query)

        return ledger


class AccountTreeSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'code', 'type', 'balance']

    def get_balance(self, instance):
        request = self.context.get("request")
        query_parameters = request.query_params
        date_after = ""
        date_before = ""
        voucher_detail = VoucherDetail.objects.all()
        if 'date_after' in query_parameters:
            date_after = query_parameters['date_after']

        if 'date_before' in query_parameters:
            date_before = query_parameters['date_before']
        if date_after:
            voucher_detail = voucher_detail.filter(created_date_ad__date__gte=date_after)
        if date_before:
            voucher_detail = voucher_detail.filter(created_date_ad__date__lte=date_before)

        total_debit = sum(voucher_detail.filter(account=instance).values_list('dr_amount', flat=True))
        total_credit = sum(voucher_detail.filter(account=instance).values_list('cr_amount', flat=True))

        return total_debit - total_credit


class AccountGroupTreeSerializer(serializers.ModelSerializer):
    accounts = AccountTreeSerializer(many=True, read_only=True)
    parent_name = serializers.ReadOnlyField(source="parent.name", allow_null=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = AccountGroup
        fields = ['id', 'level', 'parent', 'parent_name', 'accounts', 'balance']

    def get_balance(self, instance):
        request = self.context.get("request")
        query_parameters = request.query_params
        date_after = ""
        date_before = ""
        if 'date_after' in query_parameters:
            date_after = query_parameters['date_after']

        if 'date_before' in query_parameters:
            date_before = query_parameters['date_before']

        groups = instance.get_descendants(include_self=True).values_list('id', flat=True)
        accounts = Account.objects.filter(group__in=groups).values_list('id', flat=True)
        voucher_details = VoucherDetail.objects.all()
        if date_after:
            voucher_details = voucher_details.filter(created_date_ad__date__gte=date_after)
        if date_before:
            voucher_details = voucher_details.filter(created_date_ad__date__lte=date_before)
        total_credit = sum(voucher_details.filter(account__in=accounts).values_list('cr_amount', flat=True))
        total_debit = sum(voucher_details.filter(account__in=accounts).values_list('dr_amount', flat=True))

        return {"total_debit": total_debit, "total_credit": total_credit}


class ProfitAndLossReportSerializer(serializers.ModelSerializer):
    accounts = AccountTreeSerializer(many=True, read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = AccountGroup
        fields = ['id', 'name', 'balance', 'accounts']

    def get_balance(self, instance):
        request = self.context.get("request")
        query_parameters = request.query_params
        date_after = ""
        date_before = ""
        if 'date_after' in query_parameters:
            date_after = query_parameters['date_after']

        if 'date_before' in query_parameters:
            date_before = query_parameters['date_before']

        groups = instance.get_descendants(include_self=True).values_list('id', flat=True)
        accounts = Account.objects.filter(group__in=groups).values_list('id', flat=True)
        voucher_details = VoucherDetail.objects.all()
        if date_after:
            voucher_details = voucher_details.filter(created_date_ad__date__gte=date_after)
        if date_before:
            voucher_details = voucher_details.filter(created_date_ad__date__lte=date_before)
        total_credit = sum(voucher_details.filter(account__in=accounts).values_list('cr_amount', flat=True))
        total_debit = sum(voucher_details.filter(account__in=accounts).values_list('dr_amount', flat=True))

        return total_debit - total_credit


class BalanceSheetSerializer(serializers.ModelSerializer):
    accounts = AccountTreeSerializer(many=True, read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = AccountGroup
        fields = ['id', 'name', 'balance', 'accounts']

    def get_balance(self, instance):
        request = self.context.get("request")
        query_parameters = request.query_params
        date_after = ""
        date_before = ""
        if 'date_after' in query_parameters:
            date_after = query_parameters['date_after']

        if 'date_before' in query_parameters:
            date_before = query_parameters['date_before']

        groups = instance.get_descendants(include_self=True).values_list('id', flat=True)
        accounts = Account.objects.filter(group__in=groups).values_list('id', flat=True)
        voucher_details = VoucherDetail.objects.all()
        if date_after:
            voucher_details = voucher_details.filter(created_date_ad__date__gte=date_after)
        if date_before:
            voucher_details = voucher_details.filter(created_date_ad__date__lte=date_before)
        total_credit = sum(voucher_details.filter(account__in=accounts).values_list('cr_amount', flat=True))
        total_debit = sum(voucher_details.filter(account__in=accounts).values_list('dr_amount', flat=True))

        return total_debit - total_credit
