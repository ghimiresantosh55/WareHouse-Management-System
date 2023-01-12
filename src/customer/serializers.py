from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import Country
from src.custom_lib.functions import current_user
from src.supplier.models import Supplier
# imported model here
from .models import Customer, CustomerIsSupplier


class CustomerSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='country.name', allow_null=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.filter(active=True),
                                                  write_only=True, required=False)

    class Meta:
        model = Customer
        exclude = ['user']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'image', 'country_name', }
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

    def create(self, validated_data):
        # provide current time
        supplier = validated_data.pop('supplier', None)
        validated_data['created_by'] = current_user.get_created_by(self.context)
        customer = Customer.objects.create(**validated_data, created_date_ad=timezone.now())
        if supplier:
            CustomerIsSupplier.objects.create(customer=customer,
                                              supplier=supplier)
        return customer

    def update(self, instance, validated_data):
        supplier = validated_data.pop('supplier', None)
        Customer.objects.filter(pk=instance.id).update(**validated_data)
        if supplier:
            try:
                customer = CustomerIsSupplier.objects.get(customer=instance)
                customer.supplier = supplier
                customer.save()
            except CustomerIsSupplier.DoesNotExist:
                CustomerIsSupplier.objects.create(customer=instance, supplier=supplier)

        return instance
