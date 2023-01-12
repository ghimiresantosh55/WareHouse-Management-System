from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.item_serialization.models import PackingTypeDetailCode, RfidTag
from .models import AssetIssue, AssetCategory, AssetSubCategory, Asset
from .models import AssetList, AssetService
from .unique_no_generator import generate_asset_re_serial
from ..warehouse_location.models import Location

User = get_user_model()


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        asset_category = AssetCategory.objects.create(**validated_data, created_date_ad=date_now)
        return asset_category


class GetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        exclude = ['active', 'created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type']


class AssetSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetSubCategory
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        asset_sub_category = AssetSubCategory.objects.create(**validated_data, created_date_ad=date_now)
        return asset_sub_category

    def to_representation(self, instance):
        """
        method for get category  object
        """
        data = super().to_representation(instance)
        if data['asset_category'] is not None:
            asset_category = AssetCategory.objects.get(id=data["asset_category"])
            category_data = GetCategorySerializer(asset_category)
            data['asset_category'] = category_data.data
        return data


class AssetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetList
        exclude = ['asset', 'location']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type']


class ListAssetListSerializer(serializers.ModelSerializer):
    serial_no = serializers.ReadOnlyField(source='packing_type_detail_code.code', allow_null=True)
    purchase_cost = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost', allow_null=True)
    purchase_date = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.created_date_ad', allow_null=True)
    asset_supplier_name = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase.supplier.name', allow_null=True)
    depreciation_amount_till_now = serializers.SerializerMethodField()
    depreciation_amount_yearly = serializers.SerializerMethodField()
    asset_current_value = serializers.SerializerMethodField()

    class Meta:
        model = AssetList
        exclude = ['asset']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type']

    def get_depreciation_amount_till_now(self, instance):
        quantize_places = Decimal(10) ** -2
        date_now = timezone.now()
        time_duration = date_now.month - instance.created_date_ad.month
        purchase_cost = instance.packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost
        purchase_cost = purchase_cost.quantize(quantize_places)
        salvage_value = instance.asset.salvage_value
        end_of_life_in_years = instance.asset.end_of_life_in_years
        time_duration_yearly = date_now.year - instance.created_date_ad.year

        if time_duration_yearly > end_of_life_in_years:
            depreciation_amount_till_now = (purchase_cost - salvage_value)
            depreciation_amount_till_now = depreciation_amount_till_now.quantize(quantize_places)

        if instance.asset.depreciation_method == 1:
            amount_calculated = (purchase_cost - salvage_value)
            depreciation_amount_yearly = (amount_calculated / end_of_life_in_years)
            depreciation_amount_till_now = (depreciation_amount_yearly / 12) * time_duration
            depreciation_amount_till_now = depreciation_amount_till_now.quantize(quantize_places)

        else:
            depreciation_rate = instance.asset.depreciation_rate
            depreciation_rate = depreciation_rate.quantize(quantize_places)
            adjusted_book_value = instance.asset.adjusted_book_value
            adjusted_book_value = adjusted_book_value.quantize(quantize_places)
            depreciation_amount_yearly = (depreciation_rate * adjusted_book_value)
            depreciation_amount_till_now = (depreciation_amount_yearly / 12) * time_duration
            depreciation_amount_till_now = depreciation_amount_till_now.quantize(quantize_places)
        return depreciation_amount_till_now.quantize(quantize_places)

    def get_depreciation_amount_yearly(self, instance):
        quantize_places = Decimal(10) ** -2
        purchase_cost = instance.packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost
        salvage_value = instance.asset.salvage_value
        end_of_life_in_years = instance.asset.end_of_life_in_years
        if instance.asset.depreciation_method == 1:
            amount_calculated = (purchase_cost - salvage_value)
            amount_calculated = amount_calculated.quantize(quantize_places)
            depreciation_amount_yearly = (amount_calculated / end_of_life_in_years)
            depreciation_amount_yearly.quantize(quantize_places)


        else:
            depreciation_amount_yearly = (instance.asset.depreciation_rate * instance.asset.adjusted_book_value)

        return depreciation_amount_yearly.quantize(quantize_places)

    def get_asset_current_value(self, instance):
        date_now = timezone.now()
        quantize_places = Decimal(10) ** -2
        purchase_cost = instance.packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost
        salvage_value = instance.asset.salvage_value
        end_of_life_in_years = instance.asset.end_of_life_in_years
        time_duration = date_now.month - instance.created_date_ad.month
        if instance.asset.depreciation_method == 1:
            amount_calculated = (purchase_cost - salvage_value)
            amount_calculated = amount_calculated.quantize(quantize_places)
            depreciation_amount_yearly = (amount_calculated / end_of_life_in_years)
            depreciation_amount_yearly = depreciation_amount_yearly.quantize(quantize_places)
            depreciation_amount = (depreciation_amount_yearly / 12) * time_duration
            depreciation_amount = depreciation_amount.quantize(quantize_places)
            asset_current_value = purchase_cost - depreciation_amount
        else:
            depreciation_rate = instance.asset.depreciation_rate
            depreciation_rate = depreciation_rate.quantize(quantize_places)
            adjusted_book_value = instance.asset.adjusted_book_value
            adjusted_book_value = adjusted_book_value.quantize(quantize_places)
            depreciation_amount_yearly = (depreciation_rate * adjusted_book_value) * time_duration
            depreciation_amount_yearly = depreciation_amount_yearly.quantize(quantize_places)
            depreciation_amount = (depreciation_amount_yearly / 12) * time_duration
            depreciation_amount = depreciation_amount.quantize(quantize_places)
            asset_current_value = purchase_cost - depreciation_amount
            asset_current_value = asset_current_value.quantize(quantize_places)

        return asset_current_value.quantize(quantize_places)


class GetAssetSerializer(serializers.ModelSerializer):
    asset_details = ListAssetListSerializer(many=True)
    asset_item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    asset_category_name = serializers.ReadOnlyField(source='category.name', allow_null=True)
    asset_sub_category_name = serializers.ReadOnlyField(source='sub_category.name', allow_null=True)
    asset_item_manufacturer_name = serializers.ReadOnlyField(source='item.manufacturer.name', allow_null=True)
    asset_item_model_no = serializers.ReadOnlyField(source='item.model_no', allow_null=True)
    asset_location_code = serializers.ReadOnlyField(source='location.code', allow_null=True)
    issued = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        exclude = ["bulk_update"]

    def get_issued(self, instance):
        last_issue = AssetIssue.objects.filter(asset=instance.id).order_by("id").last()
        if last_issue:
            if last_issue.issue_type == 1:
                return True
            else:
                return False
        else:
            return False


class AssetSerializer(serializers.ModelSerializer):
    asset_details = AssetListSerializer(many=True)

    class Meta:
        model = Asset
        exclude = ["bulk_update"]
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'device_type', 'app_type',
                            'registration_no']

    def create(self, validated_data):
        quantize_places = Decimal(10) ** -2
        for asset_detail in validated_data['asset_details']:
            purchase_cost = asset_detail['packing_type_detail_code'].pack_type_code.purchase_detail.purchase_cost

        salvage_value = validated_data['salvage_value']
        end_of_life_in_years = validated_data['end_of_life_in_years']
        if purchase_cost < validated_data['salvage_value']:
            raise serializers.ValidationError({
                "msg": f"Salvage value should be less than purchase cost : {purchase_cost}"
            })
        amount_calculated = (purchase_cost - salvage_value)
        amount_calculated = amount_calculated.quantize(quantize_places)

        # if validated_data['depreciation_rate'] == "":
        #     validated_data["depreciation_rate"] = (amount_calculated / purchase_cost) * Decimal('100')
        #     validated_data["depreciation_rate"] = validated_data["depreciation_rate"].quantize(quantize_places)

        if validated_data['depreciation_method'] == 1:
            depreciation_amount = amount_calculated / end_of_life_in_years
            validated_data["depreciation_rate"] = (depreciation_amount / purchase_cost) * Decimal('100')
            validated_data["depreciation_rate"] = validated_data["depreciation_rate"].quantize(quantize_places)

        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        asset_details = validated_data.pop('asset_details')

        asset_main = Asset.objects.create(**validated_data, created_date_ad=date_now,
                                          registration_no=generate_asset_re_serial())

        for asset_detail in asset_details:
            AssetList.objects.create(**asset_detail, asset=asset_main, created_date_ad=date_now,
                                     created_by=validated_data['created_by'])
        return asset_main


class AssetListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'remarks', 'salvage_value', 'depreciation_rate', 'amc_rate', 'depreciation_method',
                  'end_of_life_in_years', 'warranty_duration', 'maintenance_duration']


class ListCreateAssetListSerializer(serializers.Serializer):
    asset = AssetListCreateSerializer()
    serial_nos = serializers.ListSerializer(
        child=serializers.PrimaryKeyRelatedField(
            queryset=PackingTypeDetailCode.objects.all()
        )
    )

    def create(self, validated_data):
        created_by = current_user.get_created_by(self.context)
        created_date_ad = timezone.now()
        asset_data = validated_data.pop("asset")
        serial_nos = validated_data.pop('serial_nos')
        for serial in serial_nos:
            Asset.objects.create(
                packing_type_detail_code=serial,
                scrapped=False, available=True,
                remarks=asset_data['remarks'],
                salvage_value=asset_data['salvage_value'],
                depreciation_rate=asset_data['depreciation_rate'],
                amc_rate=asset_data['amc_rate'],
                depreciation_method=asset_data['depreciation_method'],
                end_of_life_in_years=asset_data['end_of_life_in_years'],
                warranty_duration=asset_data['warranty_duration'],
                maintenance_duration=asset_data['maintenance_duration'],
                created_by=created_by, created_date_ad=created_date_ad
            )
        return validated_data


class AssetListViewSerializer(serializers.ModelSerializer):
    serial_no = serializers.ReadOnlyField(source='packing_type_detail_code.code', allow_null=True)
    category = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.item.item_category.name', allow_null=True)
    asset_item_name = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.item.name', allow_null=True)
    asset_item_category = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.item_category.name', allow_null=True)
    asset_item_depreciation_rate = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.item.depreciation_rate', allow_null=True)
    asset_item_depreciation_year = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.item.depreciation_year', allow_null=True)
    asset_item_salvage_value = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.item.salvage_value', allow_null=True)
    asset_item_manufacturer_name = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.item.manufacturer.name', allow_null=True)
    issued = serializers.SerializerMethodField()

    class Meta:
        model = AssetList
        fields = "__all__"

    def get_issued(self, instance):
        last_issue = AssetIssue.objects.filter(asset=instance.id).order_by("id").last()
        if last_issue:
            if last_issue.issue_type == 1:
                return True
            else:
                return False
        else:
            return False


class AssetIssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetIssue
        fields = ['asset', 'issued_to', 'due_date_ad', 'due_date_bs']
        read_only_fields = ['due_date_bs']

    def create(self, validated_data):
        validated_data['issue_type'] = 1  # default ISSUED = 1
        validated_data['created_by'] = current_user.get_created_by(self.context)
        validated_data['created_date_ad'] = timezone.now()
        asset_issue = AssetIssue.objects.create(**validated_data)
        return asset_issue


class AssetIssueReturnSerializer(serializers.Serializer):
    asset_issue_id = serializers.PrimaryKeyRelatedField(queryset=AssetIssue.objects.filter(issue_type=1))
    return_received_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    remarks = serializers.CharField(max_length=100, allow_blank=True)

    def create(self, validated_data):
        AssetIssue.objects.update(
            return_received_by=validated_data['return_received_by'],
            return_date_ad=timezone.now(),
            remarks=validated_data['remarks'],
            issue_type=2  # 2 = RETURNED
        )
        return validated_data


class AssetIssueListSerializer(serializers.ModelSerializer):
    asset_item_name = serializers.ReadOnlyField(
        source='asset.packing_type_detail_code.pack_type_code.purchase_detail.item.name', allow_null=True)
    asset_issued_to_first_name = serializers.ReadOnlyField(source='issued_to.first_name', allow_null=True)
    asset_issued_to_last_name = serializers.ReadOnlyField(source='issued_to.last_name', allow_null=True)
    asset_issued_to_user_name = serializers.ReadOnlyField(source='issued_to.user_name', allow_null=True)
    asset_packing_type_detail_code = serializers.ReadOnlyField(
        source="asset.packing_type_detail_code.code", allow_null=True
    )

    class Meta:
        model = AssetIssue
        fields = "__all__"


class AssetServiceSerializer(serializers.ModelSerializer):
    asset_item_name = serializers.ReadOnlyField(
        source='asset.packing_type_detail_code.pack_type_code.purchase_detail.item.name', allow_null=True)

    class Meta:
        model = AssetService
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'service_status', 'receive_date_ad',
                            'receive_date_bs',
                            'taken_by']

    def create(self, validated_data):
        validated_data['service_status'] = 1
        validated_data['created_by'] = current_user.get_created_by(self.context)
        validated_data['created_date_ad'] = timezone.now()
        asset_service = AssetService.objects.create(**validated_data)
        return asset_service


"""""""******************   Reports   *****************"""""""""""""


class AssetDetailReportSerializer(serializers.ModelSerializer):
    """
    serializer for get asset detail data
    """
    asset_id = serializers.ReadOnlyField(source='asset.id', allow_null=True)
    asset_item_name = serializers.ReadOnlyField(source='asset.item.name', allow_null=True)
    asset_registration_no = serializers.ReadOnlyField(source='asset.registration_no', allow_null=True)
    asset_supplier_name = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase.supplier.name', allow_null=True)
    asset_category_name = serializers.ReadOnlyField(source='asset.category.name', allow_null=True)
    asset_sub_category_name = serializers.ReadOnlyField(source='asset.sub_category.name', allow_null=True)
    asset_qty = serializers.ReadOnlyField(source='asset.qty', allow_null=True)
    asset_life_in_years = serializers.ReadOnlyField(source='asset.end_of_life_in_years', allow_null=True)
    asset_salvage_value = serializers.ReadOnlyField(source='asset.salvage_value', allow_null=True)
    depreciation_method_display = serializers.ReadOnlyField(source='asset.get_depreciation_method_display',
                                                            allow_null=True)
    asset_item_manufacturer_name = serializers.ReadOnlyField(source='asset.item.manufacturer.name', allow_null=True)
    asset_item_model_no = serializers.ReadOnlyField(source='asset.item.model_no', allow_null=True)
    issued = serializers.SerializerMethodField()
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    created_by_first_name = serializers.ReadOnlyField(source='created_by.first_name')
    created_by_middle_name = serializers.ReadOnlyField(source='created_by.middle_name')
    created_by_last_name = serializers.ReadOnlyField(source='created_by.last_name')
    depreciation_amount_till_now = serializers.SerializerMethodField()
    depreciation_amount_yearly = serializers.SerializerMethodField()
    asset_current_value = serializers.SerializerMethodField()
    serial_no = serializers.ReadOnlyField(source='packing_type_detail_code.code', allow_null=True)
    purchase_cost = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost', allow_null=True)
    purchase_date = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.created_date_ad', allow_null=True)

    class Meta:
        model = AssetList
        exclude = ['asset']

    def get_issued(self, instance):
        last_issue = AssetIssue.objects.filter(asset=instance.id).order_by("id").last()
        if last_issue:
            if last_issue.issue_type == 1:
                return True
            else:
                return False
        else:
            return False

    def get_depreciation_amount_till_now(self, instance):
        date_now = timezone.now()
        quantize_places = Decimal(10) ** -2
        time_duration = date_now.month - instance.created_date_ad.month
        purchase_cost = instance.packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost
        salvage_value = instance.asset.salvage_value
        end_of_life_in_years = instance.asset.end_of_life_in_years
        time_duration_yearly = date_now.year - instance.created_date_ad.year

        if time_duration_yearly > end_of_life_in_years:
            depreciation_amount_till_now = (purchase_cost - salvage_value)

        if instance.asset.depreciation_method == 1:
            amount_calculated = (purchase_cost - salvage_value)
            depreciation_amount_yearly = (amount_calculated / end_of_life_in_years)
            depreciation_amount_till_now = (depreciation_amount_yearly / 12) * time_duration

        else:
            depreciation_amount_yearly = (instance.asset.depreciation_rate * instance.asset.adjusted_book_value)
            depreciation_amount_till_now = (depreciation_amount_yearly / 12) * time_duration

        return depreciation_amount_till_now.quantize(quantize_places)

    def get_depreciation_amount_yearly(self, instance):
        quantize_places = Decimal(10) ** -2
        purchase_cost = instance.packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost
        salvage_value = instance.asset.salvage_value
        end_of_life_in_years = instance.asset.end_of_life_in_years
        if instance.asset.depreciation_method == 1:
            amount_calculated = (purchase_cost - salvage_value)
            depreciation_amount_yearly = (amount_calculated / end_of_life_in_years)

        else:
            depreciation_amount_yearly = (instance.asset.depreciation_rate * instance.asset.adjusted_book_value)

        return depreciation_amount_yearly.quantize(quantize_places)

    def get_asset_current_value(self, instance):
        quantize_places = Decimal(10) ** -2
        date_now = timezone.now()
        purchase_cost = instance.packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost
        salvage_value = instance.asset.salvage_value
        end_of_life_in_years = instance.asset.end_of_life_in_years
        time_duration = date_now.month - instance.created_date_ad.month
        if instance.asset.depreciation_method == 1:
            amount_calculated = (purchase_cost - salvage_value)
            depreciation_amount_yearly = (amount_calculated / end_of_life_in_years)
            depreciation_amount = (depreciation_amount_yearly / 12) * time_duration
            # if time_duration > end_of_life_in_years:
            asset_current_value = purchase_cost - depreciation_amount
        else:
            depreciation_amount_yearly = (
                                                 instance.asset.depreciation_rate * instance.asset.adjusted_book_value) * time_duration
            depreciation_amount = (depreciation_amount_yearly / 12) * time_duration
            # if time_duration > end_of_life_in_years:
            asset_current_value = purchase_cost - depreciation_amount

        return asset_current_value.quantize(quantize_places)


class AssetMainSummaryReportSerializer(serializers.ModelSerializer):
    asset_item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    asset_category_name = serializers.ReadOnlyField(source='category.name', allow_null=True)
    asset_sub_category_name = serializers.ReadOnlyField(source='sub_category.name', allow_null=True)
    asset_item_manufacturer_name = serializers.ReadOnlyField(source='item.manufacturer.name', allow_null=True)
    asset_item_purchase_cost = serializers.ReadOnlyField(source='item.purchase_cost', allow_null=True)
    asset_item_model_no = serializers.ReadOnlyField(source='item.model_no', allow_null=True)
    created_by_user_name = serializers.CharField(source='created_by.user_name')
    created_by_first_name = serializers.CharField(source='created_by.first_name')
    created_by_middle_name = serializers.CharField(source='created_by.middle_name')
    created_by_last_name = serializers.CharField(source='created_by.last_name')
    depreciation_method_display = serializers.ReadOnlyField(source='get_depreciation_method_display', allow_null=True)
    issued = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        exclude = ["bulk_update"]

    def get_issued(self, instance):
        last_issue = AssetIssue.objects.filter(asset=instance.id).order_by("id").last()
        if last_issue:
            if last_issue.issue_type == 1:
                return True
            else:
                return False
        else:
            return False


class AssetAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfidTag
        fields = '__all__'
        read_only_fields = ['created_date_ad', 'created_by', 'created_date_bs', 'pack_type_detail_code', 'last_seen_dt']

    def create(self, validated_data):
        serial_no = self.context.get('view').kwargs.get('serial_no')
        try:
            pack_type_detail = PackingTypeDetailCode.objects.get(code=serial_no,
                                                                 pack_type_code__location__isnull=False,
                                                                 packingtypedetailcode__assetlist__isnull=False)
        except PackingTypeDetailCode.DoesNotExist:
            raise serializers.ValidationError({"msg": f"Serial No : {serial_no} not found"})

        created_by = current_user.get_created_by(self.context)
        return RfidTag.objects.create(
            created_by=created_by,
            pack_type_detail_code=pack_type_detail,
            created_date_ad=timezone.now(),
            last_seen_dt=timezone.now(),
            **validated_data
        )


class AssetPackTypeDetailRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        fields = '__all__'


class AssetRfidTagsListSerializer(serializers.ModelSerializer):
    location_code = serializers.SerializerMethodField()
    created_by_user_name = serializers.CharField(source='created_by.user_name')
    created_by_first_name = serializers.CharField(source='created_by.first_name')
    created_by_middle_name = serializers.CharField(source='created_by.middle_name')
    created_by_last_name = serializers.CharField(source='created_by.last_name')
    pack_type_detail_code = serializers.SerializerMethodField()

    class Meta:
        model = RfidTag
        fields = '__all__'

    def get_pack_type_detail_code(self, instance):
        return {
            "id": instance.pack_type_detail_code.id,
            "code": instance.pack_type_detail_code.code,
            "pack_type_code": instance.pack_type_detail_code.pack_type_code.id
        }

    def get_location_code(self, instance):
        try:
            return AssetList.objects.get(packing_type_detail_code=instance.pack_type_detail_code).location.code
        except AttributeError:
            return None


class UpdateAssetListLocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetList
        fields = '__all__'


class UpdateAssetListLocationCreateSerializer(serializers.Serializer):
    rfid_tag_code = serializers.CharField(max_length=255, required=True)
    location_code = serializers.CharField(max_length=50, required=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        try:
            rfid_tag = RfidTag.objects.get(code=validated_data['rfid_tag_code'])
            asset_list = AssetList.objects.get(packing_type_detail_code=rfid_tag.pack_type_detail_code)

            try:
                location = Location.objects.get(code=validated_data['location_code'])
            except Location.DoesNotExist:
                raise serializers.ValidationError({"message": "This Location does not exist"})
            if location.is_leaf_node():
                raise serializers.ValidationError({"message": "Location is leaf node"})
            asset_list.location = location
            asset_list.save()
            validated_data['id'] = asset_list.id
        except RfidTag.DoesNotExist or AssetList.DoesNotExist:
            raise serializers.ValidationError({"message": f"Asset with this tag Id "
                                                          f": {validated_data['rfid_tag_code']} not found"})

        return validated_data


class AssetReportForDurationSerializer(serializers.ModelSerializer):
    end_of_life_years_remaining_days = serializers.SerializerMethodField()
    maintenance_duration_remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        exclude = ["bulk_update"]

    def get_maintenance_duration_remaining_days(self, instance):
        date_now = timezone.now()
        maintenance_duration = (instance.maintenance_duration * 30)
        # print(maintenance_duration, "this is maintaince period")
        created_date_ad = instance.created_date_ad
        if maintenance_duration is not None:
            time_period = date_now - created_date_ad
            if maintenance_duration > time_period:
                maintenance_duration_remaining_days = (maintenance_duration - time_period)
                pass
                return maintenance_duration_remaining_days

    def get_end_of_life_years_remaining_days(self, instance):
        date_now = timezone.now()
        end_of_life_in_years = (instance.end_of_life_in_years * 365)
        created_date_ad = instance.created_date_ad
        if end_of_life_in_years is not None:
            time_period_date = date_now - created_date_ad
            time_period = time_period_date.days
            if end_of_life_in_years > time_period:
                end_of_life_years_remaining_days = end_of_life_in_years - time_period
            else:
                pass
            return end_of_life_years_remaining_days


class AssetDetailListSerializer(serializers.ModelSerializer):
    asset_item_name = serializers.ReadOnlyField(source='asset.item.name', allow_null=True)
    serial_no = serializers.ReadOnlyField(source='packing_type_detail_code.code', allow_null=True)
    purchase_cost = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase_cost', allow_null=True)
    purchase_date = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.created_date_ad', allow_null=True)
    purchase_supplier_name = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase.supplier.name', allow_null=True)
    supplier_contact_no = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase.supplier.phone_no', allow_null=True)

    supplier_address = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase.supplier.address', allow_null=True)
    supplier_pan_no = serializers.ReadOnlyField(
        source='packing_type_detail_code.pack_type_code.purchase_detail.purchase.supplier.pan_vat_no', allow_null=True)

    class Meta:
        model = AssetList
        fields = ['id', 'serial_no', 'asset_item_name', 'purchase_cost', 'purchase_date', 'purchase_supplier_name',
                  'supplier_contact_no',
                  'supplier_address', 'supplier_pan_no']


class AssetAssignListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfidTag
        fields = '__all__'
        read_only_fields = ['created_date_ad', 'created_by', 'created_date_bs', 'pack_type_detail_code', 'last_seen_dt']


class AssetInfoListSerializer(serializers.ModelSerializer):
    asset_item_name = serializers.ReadOnlyField(source='asset.item.name', allow_null=True)
    serial_no = serializers.ReadOnlyField(source='packing_type_detail_code.code', allow_null=True)
    warranty_duration = serializers.ReadOnlyField(source='asset.warranty_duration', allow_null=True)
    maintenance_duration = serializers.ReadOnlyField(source='asset.maintenance_duration', allow_null=True)
    asset_end_of_life_in_years = serializers.ReadOnlyField(source='asset.end_of_life_in_years', allow_null=True)
    rfid_tag_codes = serializers.SerializerMethodField()

    class Meta:
        model = AssetList
        fields = ['id', 'serial_no', 'asset_item_name', 'warranty_duration', 'maintenance_duration',
                  'asset_end_of_life_in_years', 'rfid_tag_codes']

    def get_rfid_tag_codes(self, instance):
        packing_type_detail_code = instance.packing_type_detail_code
        try:
            rfid_tag_cod = RfidTag.objects.get(pack_type_detail_code=packing_type_detail_code)
            rfid_tag_codes = rfid_tag_cod.code
        except RfidTag.DoesNotExist:
            return None
        return rfid_tag_codes
