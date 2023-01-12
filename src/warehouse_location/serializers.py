from django.db.models import Count
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from src.custom_lib.functions import current_user
from src.item.models import Item
from src.item_serialization.models import PackingTypeDetailCode
from .location_unique_code_generator import generate_location_code
from .models import Location


class LocationCrateSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'prefix', 'parent', 'code', 'department', 'created_date_ad', 'created_date_bs', 'created_by']
        read_only_fields = ['code', 'created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        if validated_data.get('parent', None):
            parent_code = validated_data['parent'].code

            code = generate_location_code(validated_data['prefix'], validated_data['parent'].level,
                                          validated_data['parent'].id)
            validated_data['code'] = parent_code + "-" + code

        else:
            validated_data['code'] = generate_location_code(validated_data['prefix'], -1, None)
        user = current_user.get_created_by(self.context)
        location = Location.objects.create(**validated_data, created_date_ad=timezone.now(), created_by=user)
        return location

    def validate(self, attrs):
        if Location.objects.filter(department=attrs['department'], parent__isnull=True).exists() and attrs['parent'] == None:
            raise serializers.ValidationError(
                {"error": "warehouse of this department already exists please select parent location"}
            )
        return super(LocationCrateSerializer, self).validate(attrs)


class LocationUpdateSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'parent', 'is_active', 'remarks']
        read_only_fields = ['code', 'level']

    def update(self, instance, validated_data):
        if not instance.is_leaf_node():
            raise serializers.ValidationError({"detail": f'{instance.name} is not leaf node'})
        instance.name = validated_data.get("name", instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        if validated_data.get("parent", None):
            instance.parent = validated_data.get('parent')
            parent_code = validated_data['parent'].code

            code = generate_location_code(instance.prefix, validated_data['parent'].level, validated_data['parent'].id)
            instance.code = parent_code + "-" + code
        instance.save()
        return instance


class LocationGetSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'prefix', 'code', 'parent', 'level', 'department']


class LocationMapSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'prefix', 'code', 'department']


class LocationItemListSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'code', 'items', 'department']
        read_only_fields = fields

    @staticmethod
    def get_items(instance):
        location = Location.objects.get(id=instance.id)
        items = Item.objects.filter(purchasedetail__pu_pack_type_codes__location=location).distinct("id").values(
            "id", "name", "code"
        )
        data = []
        for item in items:
            remaining_qty = PackingTypeDetailCode.objects.filter(
                pack_type_code__purchase_detail__item=item['id'],
                pack_type_code__location=location,
                packingtypedetailcode__isnull=True
            ).annotate(
                ref_count=Count('pack_type_detail_code_of_sale') % 2
            ).filter(ref_count=0).count()
            return_data = {
                "id": item['id'],
                "name": item['name'],
                "code": item['code'],
                "remaining_qty": remaining_qty
            }
            data.append(return_data)
        return data
