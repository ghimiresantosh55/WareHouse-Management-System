from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.item_serialization.models import PackingTypeDetailCode
from .audit_no_generator import generate_audit_no
from .audit_service import generate_audit
from .models import Audit, AuditDetail, ItemAudit, ItemAuditDetail


class AuditDetailCreateSerializer(serializers.ModelSerializer):
    packing_type_detail_code = serializers.CharField(max_length=50)

    class Meta:
        model = AuditDetail
        fields = ['packing_type_detail_code']


class AuditCreateSerializer(serializers.ModelSerializer):
    audit_details = AuditDetailCreateSerializer(many=True)

    class Meta:
        model = Audit
        fields = ['id', 'audit_no', 'audit_details', 'remarks', 'is_finished']
        read_only_fields = ['audit_no']
        # extra_kwargs = {
        #     'packing_type_detail_code_nos': {'write_only': True}
        # }

    def create(self, validated_data):
        date_now = timezone.now()
        created_by_user = current_user.get_created_by(self.context)
        audit_details = validated_data.pop('audit_details')
        audit = Audit.objects.create(
            **validated_data,
            audit_no=generate_audit_no(),
            created_date_ad=date_now,
            created_by=created_by_user
        )

        for audit_detail in audit_details:
            try:
                pack_type_detail_code = PackingTypeDetailCode.objects.filter(
                    ref_packing_type_detail_code__isnull=True).get(code=audit_detail['packing_type_detail_code'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {"message": f"this : {audit_detail['packing_type_detail_code']} does not exist"})
            AuditDetail.objects.create(
                audit=audit,
                detail_type=2,
                packing_type_detail_code=pack_type_detail_code,
                created_by=audit.created_by,
                created_date_ad=audit.created_date_ad
            )

        if audit.is_finished:
            generate_audit(audit)
        return audit

    def update(self, instance, validated_data):

        audit_details = validated_data.pop('audit_details')
        instance.is_finished = validated_data.get("is_finished", instance.is_finished)
        instance.remarks = validated_data.get("remarks", instance.remarks)

        for audit_detail in audit_details:
            try:
                pack_type_detail_code = PackingTypeDetailCode.objects.get(code=audit_detail['packing_type_detail_code'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {"message": f"this : {audit_detail['packing_type_detail_code']} does not exist"})
            AuditDetail.objects.create(
                audit=instance,
                detail_type=2,
                packing_type_detail_code=pack_type_detail_code,
                created_by=instance.created_by,
                created_date_ad=instance.created_date_ad
            )

        if instance.is_finished:
            generate_audit(instance)
        return instance


class AuditReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditDetail
        fields = ['id', 'detail_type', 'packing_type_detail_code']


class AuditReportSerializer(serializers.ModelSerializer):
    audit_details = AuditReportDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Audit
        fields = ['id', 'audit_no', 'remarks', 'is_finished', 'audit_details']
        read_only_fields = fields


class SaveItemAuditDetailSerializer(serializers.ModelSerializer):
    packing_type_detail_code = serializers.CharField(max_length=50)

    class Meta:
        model = ItemAuditDetail
        fields = ['packing_type_detail_code']


def audit_compare_func(audit_data, packing_type_detail_code, item_audit):
    remaining_pack_detail_codes = list(set(packing_type_detail_code) - set(audit_data))
    # remaining_pack_detail_codes = [item for item in packing_type_detail_code if item not in audit_data]
    for data in remaining_pack_detail_codes:
        ItemAuditDetail.objects.create(
            created_by=item_audit.created_by,
            created_date_ad=item_audit.created_date_ad,
            item_audit=item_audit,
            packing_type_detail_code=data,
            audit_status=2
        )


class SaveItemAuditSerializer(serializers.ModelSerializer):
    item_audit_details = SaveItemAuditDetailSerializer(many=True, required=True)

    class Meta:
        model = ItemAudit
        fields = ['remarks', 'item', 'item_audit_details']

    def create(self, validated_data):
        item_audit_details = validated_data.pop('item_audit_details')
        date_now = timezone.now()
        created_by = current_user.get_created_by(self.context)
        item_audit = ItemAudit.objects.create(
            created_by=created_by,
            created_date_ad=date_now,
            **validated_data
        )

        packing_type_detail_codes = PackingTypeDetailCode.objects.filter(
            pack_type_code__purchase_detail__item=validated_data['item']
        )

        audit_data = []
        for detail in item_audit_details:
            try:
                packing_type_detail_code = PackingTypeDetailCode.objects.get(code=detail)
            except PackingTypeDetailCode.DoesNotExist:
                raise serializers.ValidationError({"msg": f"Packing type detail code : {detail} doesn't exist"})

            if packing_type_detail_code in packing_type_detail_codes:
                ItemAuditDetail.objects.create(
                    created_by=created_by,
                    created_date_ad=date_now,
                    item_audit=item_audit,
                    packing_type_detail_code=packing_type_detail_code,
                    audit_status=1
                )

                audit_data.append(packing_type_detail_code)

        audit_compare_func(audit_data, packing_type_detail_codes, item_audit)

        return item_audit


class GetItemAuditDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAuditDetail
        fields = '__all__'


class GetItemAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAudit
        fields = ['id', 'remarks', 'audit_no', 'item']


class GetItemAuditSummarySerializer(serializers.ModelSerializer):
    item_audit_details = GetItemAuditDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = ItemAudit
        fields = '__all__'
