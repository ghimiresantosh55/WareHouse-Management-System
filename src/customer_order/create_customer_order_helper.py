import decimal
from decimal import Decimal

from rest_framework import serializers

from src.item.services.stock_serial_no_info import (get_remaining_packing_type_detail_codes_count,
                                                    get_remaining_packing_type_detail_codes)
from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode
from src.purchase.models import PurchaseDetail


def generate_customer_order(order_details):
    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    quantize_places = decimal.Decimal(10) ** -2
    order_detail_return_data = []

    for order_detail in order_details:
        rem_item_count = get_remaining_packing_type_detail_codes_count(order_detail['item'])
        if rem_item_count < int(Decimal(order_detail['qty'])):
            raise serializers.ValidationError(
                {"message": f"item id : {order_detail['item']} have only {rem_item_count} item remaining"}
            )
        pack_type_detail_codes_of_item_ids = get_remaining_packing_type_detail_codes(
            order_detail['item']
        )[:int(Decimal(order_detail['qty']))]

        purchase_detail_ids = PurchaseDetail.objects.filter(
            pu_pack_type_codes__pack_type_detail_codes__id__in=pack_type_detail_codes_of_item_ids
        ).distinct('id').values_list('id', flat=True)
        for purchase_detail_id in purchase_detail_ids:
            qty = PackingTypeDetailCode.objects.filter(
                id__in=pack_type_detail_codes_of_item_ids,
                pack_type_code__purchase_detail=purchase_detail_id).distinct('id').count()
            gross_amount = Decimal(int(qty) * Decimal(order_detail['sale_cost'])).quantize(quantize_places)
            discount_amount = Decimal(
                Decimal(order_detail['discount_rate']) * gross_amount / 100
            ).quantize(quantize_places)
            discounted_amount = gross_amount - discount_amount
            tax_amount = Decimal(Decimal(order_detail['tax_rate']) * discounted_amount / 100).quantize(quantize_places)
            net_amount = gross_amount - discount_amount + tax_amount
            customer_order_detail_data = {
                'item': order_detail['item'],
                'item_category': order_detail['item_category'],
                'qty': qty,
                'purchase_cost': order_detail['purchase_cost'],
                'sale_cost': order_detail['sale_cost'],
                'taxable': order_detail['taxable'],
                'tax_rate': order_detail['tax_rate'],
                'tax_amount': tax_amount,
                'discountable': order_detail['discountable'],
                'discount_rate': order_detail['discount_rate'],
                'discount_amount': discount_amount,
                'gross_amount': gross_amount,
                'net_amount': net_amount,
                'cancelled': False,
                'purchase_detail': purchase_detail_id,
                'remarks': order_detail['remarks'],
                'customer_packing_types': []
            }

            packing_type_codes = PackingTypeCode.objects.filter(
                pack_type_detail_codes__in=pack_type_detail_codes_of_item_ids,
                purchase_detail=purchase_detail_id
            ).distinct("id")

            for packing_type_code in packing_type_codes:
                packing_type_code_id = packing_type_code.id
                customer_packing_types_data = {
                    "packing_type_code": packing_type_code_id,
                    "sale_packing_type_detail_code": []
                }

                packing_type_detail_codes = PackingTypeDetailCode.objects.filter(
                    pack_type_code=packing_type_code_id,
                    id__in=pack_type_detail_codes_of_item_ids
                ).distinct("id")
                for packing_type_detail in packing_type_detail_codes:
                    sale_packing_type_detail_code = {
                        "packing_type_detail_code": packing_type_detail.id
                    }
                    customer_packing_types_data['sale_packing_type_detail_code'].append(sale_packing_type_detail_code)
                customer_order_detail_data['customer_packing_types'].append(customer_packing_types_data)
            order_detail_return_data.append(customer_order_detail_data)

    return order_detail_return_data
