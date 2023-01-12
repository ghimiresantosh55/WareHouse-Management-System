from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import Country
from src.custom_lib.functions import current_user
# imported model here
from .models import Supplier
# purchase_order_serializer for supplier
from ..customer.models import Customer, CustomerIsSupplier


class SupplierSerializer(serializers.ModelSerializer):
    # image = serializer.FileField(max_length=None, allow_empty_file=True, use_url=True, required=False)
    country_name = serializers.ReadOnlyField(source='country.name', allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.filter(active=True), write_only=True,
                                                  required=False)

    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        customer = validated_data.pop('customer', None)
        validated_data['created_by'] = current_user.get_created_by(self.context)
        supplier = Supplier.objects.create(**validated_data, created_date_ad=date_now)
        if customer:
            CustomerIsSupplier.objects.create(supplier=supplier, customer=customer)
        return supplier

    def validate(self, data):
        if Supplier.objects.exclude(pan_vat_no__iexact="").filter(pan_vat_no__iexact=data['pan_vat_no']).exists():
            raise serializers.ValidationError({"pan_vat_no": f"This pan_vat_no {data['pan_vat_no']} already exist"})
        return super(SupplierSerializer, self).validate(data)

    def update(self, instance, validated_data):
        customer = validated_data.pop('customer', None)
        Supplier.objects.filter(pk=instance.id).update(**validated_data)
        if customer:
            try:
                supplier = CustomerIsSupplier.objects.get(supplier=instance)
                supplier.customer = customer
                supplier.save()
            except CustomerIsSupplier.DoesNotExist:
                CustomerIsSupplier.objects.create(customer=customer, supplier=instance)

        return instance

    def to_representation(self, instance):
        my_fields = {'image'}
        data = super().to_representation(instance)
        try:
            data['country'] = Country.objects.values('id', 'name').get(id=data['country'])
        except:
            pass
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data
