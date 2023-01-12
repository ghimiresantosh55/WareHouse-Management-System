from django.utils import timezone
from rest_framework import serializers

from .models import TaskMain, TaskDetail, PPBDetail, TaskOutput
from .unique_no_generator import generate_task_no
from ..core_app.models import FiscalSessionAD, FiscalSessionBS
from ..custom_lib.functions import current_user
from ..custom_lib.functions.current_user import get_created_by
from ..custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from ..item_serialization.models import SalePackingTypeDetailCode, PackingTypeCode, PackingTypeDetailCode
from ..item_serialization.unique_item_serials import generate_packtype_serial, generate_packtype_detail_serial
from ..purchase.models import PurchaseMaster, PurchaseDetail
from ..purchase.purchase_unique_id_generator import generate_purchase_no, generate_batch_no


class SaveTaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDetail
        fields = ['id', 'item', 'qty', 'ppb_detail', 'purchase_detail']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveTaskMainSerializer(serializers.ModelSerializer):
    task_details = SaveTaskDetailSerializer(many=True, required=True)

    class Meta:
        model = TaskMain
        exclude = ['task_no']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        date_now = timezone.now()()
        created_by = get_created_by(self.context)

        task_details = validated_data.pop('task_details')

        # Task Main Object
        task_main = TaskMain.objects.create(
            task_no=generate_task_no(),
            created_by=created_by,
            created_date_ad=date_now,
            **validated_data
        )

        for task in task_details:
            # Task Detail Object
            TaskDetail.objects.create(
                task_main=task_main,
                created_by=created_by,
                created_date_ad=date_now,
                **task
            )

    def validate(self, attrs):
        task_details = attrs['task_details']
        if not task_details or task_details is None:
            raise serializers.ValidationError({"msg": "Please provide at least one task details"})

        ppb_details = PPBDetail.objects.filter(ppb_main=attrs['ppb_main'])
        if len(task_details) != ppb_details.count():
            raise serializers.ValidationError({"msg": "Task Details doesn't match with ppb details"})

        for task in task_details:
            if task['purchase_detail'].item != task['item']:
                raise serializers.ValidationError({"msg": "Task's Item Doesn't match with purchase"})

        return attrs


class TaskMainListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMain
        fields = '__all__'


class TaskDetailListSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_code = serializers.ReadOnlyField(source='item.code', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)
    batch_no = serializers.ReadOnlyField(source='purchase_detail.batch_no', allow_null=True)
    purchase_no = serializers.ReadOnlyField(source='purchase_detail.purchase.purchase_no', allow_null=True)

    class Meta:
        model = TaskDetail
        exclude = ['app_type', 'device_type', ]


class TaskMainSummarySerializer(serializers.ModelSerializer):
    task_details = TaskDetailListSerializer(read_only=True, many=True)
    output_item_name = serializers.ReadOnlyField(source='output_item.name', allow_null=True)
    output_item_code = serializers.ReadOnlyField(source='output_item.code', allow_null=True)
    output_item_is_serializer = serializers.ReadOnlyField(source='output_item.is_serializable', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    department_name = serializers.ReadOnlyField(source='department.name', allow_null=True)
    department_code = serializers.ReadOnlyField(source='department.code', allow_null=True)

    class Meta:
        model = TaskMain
        exclude = ['app_type', 'device_type', ]


class CancelTaskMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMain
        fields = ['id', 'ppb_main', 'expected_output_qty', 'task_no',
                  'output_item', 'department', 'remarks',
                  'is_approved', 'is_cancelled']
        read_only_fields = ['id', 'ppb_main', 'expected_output_qty', 'task_no',
                            'output_item', 'department',
                            'is_approved', 'is_cancelled']

    def update(self, instance, validated_data):
        if instance.is_approved:
            raise serializers.ValidationError({"msg": "This task has already been approved"})
        task_details = TaskDetail.objects.filter(task_main=instance)
        for task_detail in task_details:
            task_detail.is_cancelled = True
            task_detail.save()

        instance.is_cancelled = True
        instance.save()

        return instance


class CancelSingleTaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDetail
        fields = ['id', 'task_main', 'item', 'qty', 'ppb_detail', 'purchase_detail',
                  'is_cancelled']
        read_only_fields = fields

    def update(self, instance, validated_data):
        instance.is_cancelled = True
        instance.save()

        return instance


class ApproveTaskMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMain
        fields = ['id', 'ppb_main', 'expected_output_qty', 'task_no',
                  'output_item', 'department', 'remarks',
                  'is_approved', 'is_cancelled']
        read_only_fields = fields


class PickupTaskSerializer(serializers.Serializer):
    task_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=TaskDetail.objects.filter(picked=False, is_cancelled=False), required=True
    )
    pack_type_detail_code_ids = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=SalePackingTypeDetailCode.objects.all()
    ))

    def create(self, validated_data):
        if not validated_data['task_detail_id'].task_main.is_approved:
            raise serializers.ValidationError({"msg": "This task hasn't been approved yet"})

        if validated_data['task_detail_id'].is_picked:
            raise serializers.ValidationError({"msg": "This task detail has already been picked"})

        if len(validated_data['pack_type_detail_code_ids']) != validated_data['task_detail_id'].qty:
            raise serializers.ValidationError({"msg": "Qty doesn't match with the provided no of codes"})

        for pack_type_detail_code in validated_data['pack_type_detail_code_ids']:
            if pack_type_detail_code.sale_packing_type_code.task_detail.id != validated_data['asset_detail_id']:
                raise serializers.ValidationError({"msg": "serial no doesn't match with the task item"})

        validated_data['task_detail_id'].picked = True
        validated_data['task_detail_id'].picked_by = current_user.get_created_by(self.context)
        validated_data['task_detail_id'].save()
        return validated_data['task_detail_id']

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "task_main": instance.task_main,
            "item": instance.item,
            "qty": instance.qty,
            "ppb_detail": instance.ppb_detail,
            "purchase_detail": instance.purchase_detail,
            "is_cancelled": instance.is_cancelled,
            "picked": instance.picked,
            "picked_by": instance.picked_by,
            "picked_by_user_name": instance.picked_by.user_name,
        }


class UpdateTaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDetail
        fields = '__all__'
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class UpdateTaskSerializer(serializers.ModelSerializer):
    task_details = UpdateTaskDetailSerializer(required=False, many=True)

    class Meta:
        model = TaskMain
        fields = ['expected_output_qty',
                  'remarks', 'task_details']

    def update(self, instance, validated_data):
        try:
            task_details = validated_data.pop('task_details')
        except KeyError:
            task_details = []

        instance.expected_output_qty = validated_data.get('expected_output_qty', instance.expected_output_qty)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.save()

        for detail in task_details:
            TaskDetail.objects.create(
                **detail,
                created_by=instance.created_by,
                created_date_ad=timezone.now(),
                task_main=instance
            )
        return instance


class SaveTaskOutputItemHelperSerializer(serializers.Serializer):
    gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)


def add_stock_to_inventory(task_output, task_output_item_detail):
    current_fiscal_session_short_ad = get_fiscal_year_code_ad()
    current_fiscal_session_short_bs = get_fiscal_year_code_bs()

    try:
        fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
        fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)
    except Exception as e:
        raise serializers.ValidationError("fiscal session does not match")

    purchase_master = PurchaseMaster.objects.create(
        purchase_type=7,
        pay_type=2,
        purchase_no=generate_purchase_no(7),
        department=task_output.task_main.department,
        fiscal_session_ad=fiscal_session_ad,
        fiscal_session_bs=fiscal_session_bs,
        created_by=task_output.created_by,
        created_date_ad=task_output.created_date_ad,
    )

    purchase_detail = PurchaseDetail.objects.create(
        created_by=task_output.created_by,
        created_date_ad=task_output.created_date_ad,
        purchase=purchase_master,
        item=task_output.item,
        item_category=task_output.item.item_category,
        purchase_cost=task_output.item.purchase_cost,
        sale_cost=task_output.item.sale_cost,
        qty=task_output.qty,
        packing_type=task_output.packing_type,
        packing_type_detail=task_output.packing_type_detail,
        tax_rate=task_output.item.tax_rate,
        taxable=task_output.item.taxable,
        discountable=task_output.item.discountable,
        expirable=task_output.item.expirable,
        gross_amount=task_output_item_detail['gross_amount'],
        net_amount=task_output_item_detail['net_amount'],
        pack_qty=task_output.packing_type_detail.pack_qty,
        batch_no=generate_batch_no(),
    )

    packing_type = PackingTypeCode.objects.create(
        created_by=task_output.created_by,
        created_date_ad=task_output.created_date_ad,
        purchase_detail=purchase_detail,
        code=generate_packtype_serial(),
        qty=task_output.qty
    )
    if task_output.item.is_serializable:
        for i in range(task_output.qty):
            PackingTypeDetailCode.objects.create(
                created_by=task_output.created_by,
                created_date_ad=task_output.created_date_ad,
                pack_type_code=packing_type,
                code=generate_packtype_detail_serial(),
            )


class SaveTaskOutputSerializer(serializers.ModelSerializer):
    task_output_item_detail = SaveTaskOutputItemHelperSerializer(write_only=True, required=True, many=False)

    class Meta:
        model = TaskOutput
        fields = ['id', 'task_main', 'qty', 'item', 'packing_type', 'packing_type_detail', 'task_output_item_detail']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        date_now = timezone.now()
        created_by = get_created_by(self.context)

        task_output_item_detail = validated_data.pop('task_output_item_detail')

        task_output = TaskOutput.objects.create(
            created_by=created_by,
            created_date_ad=date_now,
            **validated_data
        )

        # Add to stock on successful task output
        # TODO: Test Purchase Func and Manage Stock Query
        add_stock_to_inventory(task_output, task_output_item_detail)

        return validated_data


class GetTaskOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskOutput
        fields = '__all__'


class GetTaskOutputSummarySerializer(serializers.ModelSerializer):
    task_output = TaskMainSummarySerializer(many=True, read_only=True)
    packing_type = serializers.SerializerMethodField()
    packing_type_detail = serializers.SerializerMethodField()

    class Meta:
        model = TaskOutput
        fields = '__all__'

    def get_packing_type(self, instance):
        return {
            "id": instance.packing_type.id,
            "short_name": instance.packing_type.short_name,
            "active": instance.packing_type.active
        }

    def get_packing_type_detail(self, instance):
        return {
            "id": instance.packing_type_detail.id,
            "item": instance.packing_type_detail.item.id,
            "packing_type": instance.packing_type_detail.packing_type,
            "pack_qty": instance.packing_type_detail.pack_qty,
            "active": instance.packing_type_detail.active
        }
