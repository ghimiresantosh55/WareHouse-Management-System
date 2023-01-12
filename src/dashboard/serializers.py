from rest_framework import serializers
from src.customer.models import Customer


class TopCustomerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order_count = serializers.IntegerField(default=0)
    first_name = serializers.CharField(max_length=255)
    middle_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)


class TopSupplierListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    purchase_count = serializers.IntegerField(default=0)
    name = serializers.CharField(max_length=255)


class TopItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    item_sold_count = serializers.IntegerField(default=0)
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=255)


class PurchaseChartSerializer(serializers.Serializer):
    purchase_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    purchase_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    purchase_return_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    purchase_return_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    date = serializers.IntegerField()
    purchase_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    purchase_return_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)


class SaleChartSerializer(serializers.Serializer):
    sale_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    sale_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    sale_return_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    sale_return_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    date = serializers.IntegerField()
    sale_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    sale_return_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)


class ChalanChartSerializer(serializers.Serializer):
    chalan_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    chalan_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    chalan_return_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    chalan_return_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    date = serializers.IntegerField()
    chalan_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    chalan_return_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)


class CreditChartSerializer(serializers.Serializer):
    credit_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    credit_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    credit_clearance_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    credit_clearance_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    date = serializers.IntegerField()
    credit_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    credit_clearance_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)


class PartyPaymentChartSerializer(serializers.Serializer):
    party_payment_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    party_payment_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    party_payment_clearance_count = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    party_payment_clearance_cost = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    date = serializers.IntegerField()
    party_payment_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    party_payment_clearance_amount = serializers.DecimalField(decimal_places=2, default=0.00, max_digits=9)
