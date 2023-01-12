from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce

from ..models import ChalanDetail


def get_chalan_detail_returned_qty(chalan_detail_id: int) -> int:
    chalan_detail = ChalanDetail.objects.filter(
        ref_chalan_detail=chalan_detail_id
    ).aggregate(
        sum=Coalesce(Sum('qty'), 0, output_field=DecimalField())
    )
    chalan_return = chalan_detail['sum']
    return chalan_return


def get_chalan_detail_remaining_qty(chalan_detail_id: int) -> int:
    chalan_detail = ChalanDetail.objects.filter(
        ref_chalan_detail=chalan_detail_id
    ).aggregate(
        sum=Coalesce(Sum('qty'), 0, output_field=DecimalField())
    )
    chalan_return = chalan_detail['sum']
    chalan_qty = ChalanDetail.objects.get(id=chalan_detail_id).qty

    return chalan_qty - chalan_return


def get_chalan_detail_returned_amounts(chalan_detail_id: int) -> dict:
    try:
        chalan_detail_amount_data = ChalanDetail.objects.filter(
            ref_chalan_detail=chalan_detail_id
        ).values("ref_chalan_detail").annotate(
            return_discount_amount=Sum("discount_amount", output_field=DecimalField(decimal_places=2)),
            return_tax_amount=Sum("tax_amount", output_field=DecimalField(decimal_places=2)),
            return_gross_amount=Sum("gross_amount", output_field=DecimalField(decimal_places=2)),
            return_net_amount=Sum("net_amount", output_field=DecimalField(decimal_places=2)),
        ).get(ref_chalan_detail=chalan_detail_id)
        return chalan_detail_amount_data
    except ObjectDoesNotExist:

        return {
            "return_discount_amount": Decimal("0.00"),
            "return_tax_amount": Decimal("0.00"),
            "return_gross_amount": Decimal("0.00"),
            "return_net_amount": Decimal("0.00"),

        }
