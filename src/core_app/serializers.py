from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.custom_lib.functions.fiscal_year import (get_fiscal_year_code_ad, get_fiscal_year_code_bs,
                                                  get_full_fiscal_year_code_ad, get_full_fiscal_year_code_bs)
from .models import (AdditionalChargeType, AppAccessLog, Bank, BankDeposit, Country, DiscountScheme,
                     District, FiscalSessionAD, FiscalSessionBS, OrganizationRule, OrganizationSetup,
                     PaymentMode, Province, Store)
from .models import Currency

bs_year_code = get_fiscal_year_code_bs()
ad_year_code = get_fiscal_year_code_ad()
full_ad_year_code = get_full_fiscal_year_code_ad()
full_bs_year_code = get_full_fiscal_year_code_bs()


class CountrySerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = Country
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        country = Country.objects.create(**validated_data, created_date_ad=timezone.now())
        return country


class CurrencySerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = Currency
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        currency = Currency.objects.create(**validated_data, created_date_ad=timezone.now())
        return currency


class ProvinceSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = Province
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        province = Province.objects.create(**validated_data, created_date_ad=timezone.now())
        return province


class DistrictSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)
    province_name = serializers.ReadOnlyField(source='province.name', allow_null=True)

    class Meta:
        model = District
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        district = District.objects.create(**validated_data, created_date_ad=timezone.now())
        return district


class OrganizationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRule
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'phone_no_1', 'mobile_no', 'pan_no', 'owner_name', 'email', 'website_url'}

        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        # provide current time
        date_now = timezone.now()
        # providing the id of current login user
        validated_data['created_by'] = current_user.get_created_by(self.context)
        # after getting all validated data, it is posted in DB
        organization_rule = OrganizationRule.objects.create(**validated_data, created_date_ad=date_now)
        return organization_rule


class OrganizationSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSetup
        fields = "__all__"
        # read_only_fields are the fields from same model. Fields mentioned here can't be editable.
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['country'] = Country.objects.values('id', 'name').get(id=data['country'])
        except:
            pass
        return data

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        organization_setup = OrganizationSetup.objects.create(**validated_data, created_date_ad=date_now)
        return organization_setup


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        # provide current time
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        bank = Bank.objects.create(**validated_data, created_date_ad=date_now)
        return bank


class BankBankDepositNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class BankDepositViewSerializer(serializers.ModelSerializer):
    bank = BankBankDepositNestedSerializer(read_only=True, required=False)

    class Meta:
        model = BankDeposit
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'bank']


class BankDepositCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDeposit
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        bank_deposit = BankDeposit.objects.create(**validated_data, created_date_ad=date_now)
        return bank_deposit


class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        payment_mode = PaymentMode.objects.create(**validated_data, created_date_ad=date_now)
        return payment_mode


class DiscountSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        discount_scheme = DiscountScheme.objects.create(**validated_data, created_date_ad=date_now)
        return discount_scheme


class AdditionalChargeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalChargeType
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        charge_type = AdditionalChargeType.objects.create(**validated_data, created_date_ad=date_now)
        return charge_type


class AppAccessLogSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)
    device_type_display = serializers.ReadOnlyField(source="get_device_type_display", allow_null=True)
    app_type_display = serializers.ReadOnlyField(source="get_app_type_display", allow_null=True)

    class Meta:
        model = AppAccessLog
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        if validated_data['code'] == "":
            store_count = Store.objects.count()
            max_id = str(store_count + 1)
            unique_id = "ST-" + max_id.zfill(4)
            validated_data['code'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        store = Store.objects.create(**validated_data, created_date_ad=date_now)
        return store


class FiscalSessionADSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionAD
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        if validated_data['session_short'] == "":
            unique_id = ad_year_code
            validated_data['session_short'] = unique_id

        if validated_data['session_full'] == "":
            unique_id = full_ad_year_code
            validated_data['session_full'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        fiscal_session_ad = FiscalSessionAD.objects.create(**validated_data, created_date_ad=date_now)
        return fiscal_session_ad


class FiscalSessionBSSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionBS
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        if validated_data['session_short'] == "":
            unique_id = bs_year_code
            validated_data['session_short'] = unique_id
        if validated_data['session_full'] == "":
            unique_id = full_bs_year_code
            validated_data['session_full'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        fiscal_session_bs = FiscalSessionBS.objects.create(**validated_data, created_date_ad=date_now)
        return fiscal_session_bs


class PaymentModeCoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id', 'name']
