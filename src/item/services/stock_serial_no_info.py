from django.db.models import Count

from src.item_serialization.models import PackingTypeDetailCode


def get_remaining_packing_type_detail_codes(item_id: int) -> list:
    pk_type_detail_codes = PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        pack_type_code__purchase_detail__item=item_id,
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0).order_by("id").values_list("id", flat=True)
    return pk_type_detail_codes


def get_remaining_packing_type_detail_codes_count(item_id: int) -> int:
    remaining = PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        pack_type_code__purchase_detail__item=item_id,
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0).order_by("id").values("id").count()

    return remaining


