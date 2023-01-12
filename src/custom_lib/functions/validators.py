from rest_framework import serializers
from .stock import get_purchase_qty, get_purchase_sale_qty
from django.core.exceptions import ValidationError
from rest_framework.serializers import Serializer

# when patch operation is performed for purchase details. Validation of quantity is done through this operation
def purchase_opening_stock_qty_patch_validator(purchase_detail_id,update_qty):
    sale_qty= get_purchase_sale_qty(purchase_detail_id)
    if update_qty<sale_qty:
        raise serializers.ValidationError(f"purchase_opening_stock_qty_update: {update_qty} cannot be less than sale_qty: {sale_qty}")

