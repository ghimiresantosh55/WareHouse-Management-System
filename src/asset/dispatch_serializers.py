from django.utils import timezone
from rest_framework import serializers

from .models import (AssetDispatch, AssetDispatchDetail, AssetMaintenance, AssetTransfer)
from .unique_no_generator import generate_asset_dispatch_no_serial
from ..custom_lib.functions import current_user
from ..item_serialization.models import PackingTypeDetailCode


class AssetDispatchDetailPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDispatchDetail
        exclude = ['ref_dispatch_detail', 'asset_dispatch']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class AssetMaintenancePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetMaintenance
        exclude = ['asset_dispatch', 'maintenance_no']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class AssetTransferPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTransfer
        fields = ['remarks']


class AssetDispatchPostSerializer(serializers.ModelSerializer):
    asset_dispatches = AssetDispatchDetailPostSerializer(many=True, required=True)
    asset_transfer = AssetTransferPostSerializer(many=False, required=False)
    asset_maintenance = AssetMaintenancePostSerializer(many=False, required=False)

    class Meta:
        model = AssetDispatch
        fields = ['receiver_name', 'receiver_id_no', 'dispatch_type', 'dispatch_info',
                  'dispatch_sub_type', 'dispatch_by', 'dispatch_to', 'asset_dispatches',
                  'created_date_ad', 'created_date_bs', 'created_by', 'dispatch_no', 'asset_transfer',
                  'asset_maintenance']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'dispatch_no']

    def create(self, validated_data):
        asset_dispatches = validated_data.pop('asset_dispatches')
        created_by = current_user.get_created_by(self.context)
        date_now = timezone.now()

        if validated_data['dispatch_type'] == 2:
            if validated_data['dispatch_sub_type'] is None or not validated_data['dispatch_sub_type']:
                raise serializers.ValidationError("Please provide dispatch sub type for external dispatch")

        asset_dispatch = AssetDispatch.objects.create(
            dispatch_no=generate_asset_dispatch_no_serial(1),
            created_date_ad=date_now,
            created_by=created_by,
            **validated_data
        )

        for asset in asset_dispatches:
            AssetDispatchDetail.objects.create(
                asset_dispatch=asset_dispatch,
                created_date_ad=date_now,
                created_by=created_by,
                **asset
            )

        if validated_data['dispatch_type'] == 2:
            if validated_data['dispatch_sub_type'] == 1:
                try:
                    asset_maintenance = validated_data.pop('asset_maintenance')
                    AssetMaintenance.objects.create(created_by=created_by,
                                                    created_date_ad=date_now,
                                                    **asset_maintenance)
                except KeyError:
                    raise serializers.ValidationError("asset_maintenance is required for MAINTENANCE sub type")
                else:
                    try:
                        asset_transfer = validated_data.pop('asset_transfer')
                        AssetTransfer.objects.create(created_by=created_by,
                                                     created_date_ad=date_now,
                                                     **asset_transfer)
                    except KeyError:
                        raise serializers.ValidationError("asset_transfer is required for TRANSFER sub type")
        return asset_dispatch


class AssetDispatchDetailListSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = AssetDispatchDetail
        fields = '__all__'


class AssetMaintenanceListSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = AssetMaintenance
        fields = '__all__'


class AssetTransferListSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = AssetTransfer
        fields = '__all__'


class AssetDispatchListSerializer(serializers.ModelSerializer):
    asset_dispatches = AssetDispatchDetailListSerializer(many=True, read_only=True)
    dispatch_info_display = serializers.ReadOnlyField(source='get_dispatch_info_display', allow_null=True)
    dispatch_type_display = serializers.ReadOnlyField(source='get_dispatch_type_display', allow_null=True)
    dispatch_sub_type_display = serializers.ReadOnlyField(source='get_dispatch_sub_type_display', allow_null=True)
    dispatch_to_user_name = serializers.ReadOnlyField(source='dispatch_to.user_name', allow_null=True)
    dispatch_by_user_name = serializers.ReadOnlyField(source='dispatch_by.user_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = AssetDispatch
        fields = '__all__'


class AssetDispatchDetailReturnSerializer(serializers.ModelSerializer):
    ref_dispatch_detail = serializers.PrimaryKeyRelatedField(
        queryset=AssetDispatchDetail.objects.filter(ref_dispatch_detail__isnull=True)
    )

    class Meta:
        model = AssetDispatchDetail
        exclude = ['asset_dispatch']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class AssetDispatchReturnSerializer(serializers.ModelSerializer):
    asset_dispatches = AssetDispatchDetailReturnSerializer(many=True)
    ref_dispatch = serializers.PrimaryKeyRelatedField(
        queryset=AssetDispatch.objects.filter(dispatch_info=1)
    )

    class Meta:
        model = AssetDispatch
        fields = '__all__'
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'dispatch_no']

    def create(self, validated_data):
        created_by = current_user.get_created_by(self.context)
        date_now = timezone.now()

        asset_dispatches = validated_data.pop('asset_dispatches')
        if not asset_dispatches:
            serializers.ValidationError("Please provide at least one asset dispatch detail")
        asset_dispatch = AssetDispatch.objects.create(**validated_data,
                                                      created_by=created_by,
                                                      created_date_ad=date_now)

        for asset in asset_dispatches:
            AssetDispatchDetail.objects.create(asset_dispatch=asset_dispatch,
                                               created_by=created_by,
                                               created_date_ad=date_now,
                                               **asset)

        return asset_dispatch


class PickUpAssetDispatchSerializer(serializers.Serializer):
    asset_dispatch = serializers.PrimaryKeyRelatedField(queryset=AssetDispatchDetail.objects
                                                        .filter(picked=False), required=True)
    pack_type_detail_code_id = serializers.PrimaryKeyRelatedField(queryset=PackingTypeDetailCode.objects.all())

    def create(self, validated_data):
        if validated_data['asset_dispatch'].picked:
            raise serializers.ValidationError("This asset dispatch detail has already been picked")

        if validated_data['pack_type_detail_code_id'] != validated_data['asset_dispatch'].\
                asset_detail.packing_type_detail_code:
            raise serializers.ValidationError("Serial no does not match with the asset item")

        validated_data['picked'] = True
        validated_data['picked_by'] = current_user.get_created_by(self.context)
        validated_data['asset_dispatch'].save()

        return validated_data['asset_dispatch']
