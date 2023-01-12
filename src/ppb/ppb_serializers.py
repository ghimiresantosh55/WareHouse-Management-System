from django.utils import timezone
from rest_framework import serializers

from .models import PPBMain, PPBDetail
from ..custom_lib.functions.current_user import get_created_by
from .unique_no_generator import generate_ppb_no, generate_task_no


class SavePPBMDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPBDetail
        exclude = ['ppb_main', ]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'active']


class SavePPBMainSerializer(serializers.ModelSerializer):
    ppb_details = SavePPBMDetailSerializer(many=True)

    class Meta:
        model = PPBMain
        fields = ['name', 'ppb_details', 'remarks', 'output_item']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'ppb_no']

    def create(self, validated_data):
        date_now = timezone.now()
        created_by = get_created_by(context_with_request=self.context)

        ppb_details = validated_data.pop('ppb_details')
        ppb_main = PPBMain.objects.create(
            created_by=created_by,
            created_date_ad=date_now,
            ppb_no=generate_ppb_no(),
            **validated_data
        )

        for detail in ppb_details:
            PPBDetail.objects.create(
                **detail,
                created_date_ad=date_now,
                created_by=created_by,
                ppb_main=ppb_main
            )

        return ppb_main


class PPBMainListSerializer(serializers.ModelSerializer):
    output_item_name = serializers.ReadOnlyField(source='output_item.name', allow_null=True)
    output_item_code = serializers.ReadOnlyField(source='output_item.code', allow_null=True)
    output_item_is_serializer = serializers.ReadOnlyField(source='output_item.is_serializable', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    output_item_unit_name = serializers.ReadOnlyField(source='output_item.unit.name', allow_null=True)
    output_item_unit_short_form = serializers.ReadOnlyField(source='output_item.unit.short_form', allow_null=True)

    class Meta:
        model = PPBMain
        exclude = ['app_type', 'device_type', ]


class PPBDetailListSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_code = serializers.ReadOnlyField(source='item.code', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)
    item_unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    item_unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)

    class Meta:
        model = PPBDetail
        exclude = ['app_type', 'device_type', ]


class PPBMainSummarySerializer(serializers.ModelSerializer):
    ppb_details = PPBDetailListSerializer(read_only=True, many=True)
    output_item_is_serializer = serializers.ReadOnlyField(source='output_item.is_serializable', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    output_item_unit_name = serializers.ReadOnlyField(source='output_item.unit.name', allow_null=True)
    output_item_unit_short_form = serializers.ReadOnlyField(source='output_item.unit.short_form', allow_null=True)
    output_item = serializers.SerializerMethodField()

    class Meta:
        model = PPBMain
        exclude = ['app_type', 'device_type', ]

    def get_output_item(self, instance):
        return {
            "id": instance.output_item.id,
            "name": instance.output_item.name,
            "code": instance.output_item.code,
        }

class PPBDetailDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPBDetail
        fields = '__all__'


class UpdatePPBDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPBDetail
        fields = '__all__'
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'ppb_main']


class UpdatePPBMainSerializer(serializers.ModelSerializer):
    ppb_details = UpdatePPBDetailSerializer(required=False, many=True)

    class Meta:
        model = PPBMain
        fields = ['name', 'active', 'output_item', 'remarks', 'ppb_details']

    def update(self, instance, validated_data):
        try:
            ppb_details = validated_data.pop('ppb_details')
        except KeyError:
            ppb_details = []

        instance.name = validated_data.get('name', instance.name)
        instance.active = validated_data.get('active', instance.active)
        instance.output_item = validated_data.get('output_item', instance.output_item)
        instance.remarks = validated_data.get('remarks', instance.remarks)

        instance.save()
        for ppb_detail in ppb_details:
            PPBDetail.objects.create(
                **ppb_detail,
                created_date_ad=timezone.now(),
                created_by=instance.created_by,
                ppb_main=instance
            )
        return instance
