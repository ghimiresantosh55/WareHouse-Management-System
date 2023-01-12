from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from .listing_apis import listing_serializers
# imported model here
from .models import GenericName, Item, ItemCategory, Manufacturer, PackingType, PackingTypeDetail, Unit


class PackingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingType
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        packing_type = PackingType.objects.create(**validated_data, created_date_ad=date_now)
        return packing_type


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        unit = Unit.objects.create(**validated_data, created_date_ad=date_now)
        return unit


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        manufacturer = Manufacturer.objects.create(**validated_data, created_date_ad=date_now)
        return manufacturer


class GenericNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericName
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        generic_name = GenericName.objects.create(**validated_data, created_date_ad=date_now)
        return generic_name


class SaveItemPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)

    class Meta:
        model = PackingTypeDetail
        exclude = ['item', 'packing_type', 'pack_qty', 'active']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class ItemSerializer(serializers.ModelSerializer):
    # packing_type_details =  SaveItemPackingTypeDetailSerializer(many=True)
    item_category_name = serializers.ReadOnlyField(source="item_category.name", allow_null=True)
    item_type_display = serializers.ReadOnlyField(source="get_item_type_display", allow_null=True)
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name", allow_null=True)
    generic_name_name = serializers.ReadOnlyField(source="generic_name.name", allow_null=True)
    unit_name = serializers.ReadOnlyField(source="unit.name", allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source="unit.short_form", allow_null=True)

    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ['item_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'item_category', 'unit_name', 'unit_short_form', 'image',
                     'item_category_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        if validated_data['code'] == "":
            item_count = Item.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ITM-" + max_id.zfill(36)
            validated_data['code'] = unique_id

        pack_qty = 1
        active = True
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        item = Item.objects.create(**validated_data, created_date_ad=date_now)
        PackingTypeDetail.objects.create(item=item, pack_qty=pack_qty, packing_type_id=1, active=active,
                                         created_date_ad=date_now,
                                         created_by=current_user.get_created_by(self.context)).save()
        return item


class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ['item_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'item_category', 'unit_name', 'unit_short_form', 'image',
                     'item_category_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        if validated_data['code'] == "":
            item_count = Item.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ITM-" + max_id.zfill(10)
            validated_data['code'] = unique_id
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()

        item = Item.objects.create(**validated_data, created_date_ad=date_now)
        packing_type = PackingType.objects.filter(name__iexact="unit")

        if packing_type.exists():
            packing_type = packing_type.first()
        else:
            packing_type = PackingType.objects.create(name="Unit", short_name="UNIT",
                                                      created_date_ad=date_now, created_by=validated_data['created_by'])

        PackingTypeDetail.objects.create(item=item, pack_qty=1, packing_type=packing_type, active=True,
                                         created_date_ad=date_now,
                                         created_by=current_user.get_created_by(self.context))
        return item


class ItemViewSerializer(serializers.ModelSerializer):
    item_category = listing_serializers.ItemItemCategoryListSerializer()
    manufacturer = listing_serializers.ItemManufacturerListSerializer()
    generic_name = listing_serializers.ItemGenericNameListSerializer()
    unit = listing_serializers.ItemUnitListSerializer()

    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ['item_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'item_category', 'unit_name', 'unit_short_form', 'image',
                     'item_category_name', 'basic_info', 'location'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        # empty field for display order
        if validated_data['display_order'] == '':
            validated_data['display_order'] = None
        if validated_data['code'] == "" or validated_data['code'] is None:
            item_count = ItemCategory.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ITC-" + max_id.zfill(6)
            validated_data['code'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        item_category = ItemCategory.objects.create(**validated_data, created_date_ad=date_now)
        return item_category


class PackingTypeDetailItemNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'code']


class PackingTypeDetailPackingTypeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingType
        fields = ['id', 'name', 'short_name']


class PackingTypeDetailViewSerializer(serializers.ModelSerializer):
    item = PackingTypeDetailItemNestedSerializer(read_only=True)
    packing_type = PackingTypeDetailPackingTypeNestedSerializer(read_only=True)

    class Meta:
        model = PackingTypeDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        packing_type_details = PackingTypeDetail.objects.create(**validated_data, created_date_ad=date_now)
        return packing_type_details

    def to_representation(self, instance):
        my_fields = {'unit_name', 'unit_short_form'}

        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class PackingTypeDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        packing_type_details = PackingTypeDetail.objects.create(**validated_data, created_date_ad=date_now)
        return packing_type_details

    def to_representation(self, instance):
        my_fields = {'unit_name', 'unit_short_form'}

        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class PackingTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        packing_type_details = PackingTypeDetail.objects.create(**validated_data, created_date_ad=date_now)
        return packing_type_details

    def to_representation(self, instance):
        my_fields = {'unit_name', 'unit_short_form'}

        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


"""************************** Serializers for Get Views *****************************************"""


class GetItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active', 'display_order']


class GetPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)

    class Meta:
        model = PackingTypeDetail
        exclude = ['created_date_ad', 'created_date_bs', 'active', 'created_by']


class GetManufactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        exclude = ['created_date_ad', 'created_date_bs', 'active', 'created_by']


class GetManufactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        exclude = ['created_date_ad', 'created_date_bs', 'active', 'created_by']


class GetGenericNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericName
        exclude = ['created_date_ad', 'created_date_bs', 'active', 'created_by']


class GetUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        exclude = ['created_date_ad', 'created_date_bs', 'active', 'created_by', 'display_order']