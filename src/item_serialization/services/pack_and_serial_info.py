from decimal import Decimal

from django.db.models import OuterRef, F, Count, Exists, Sum, Q, Subquery, DecimalField
from django.db.models.functions import Coalesce

from src.item_serialization.models import PackingTypeCode, PackingTypeDetailCode, SalePackingTypeCode


def find_available_serializable_pack(purchase_detail_id: int = None) -> PackingTypeCode.objects.none():
    pack_type_detail = PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        pack_type_code=OuterRef("id"),
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0)

    if purchase_detail_id is not None:

        queryset = PackingTypeCode.objects.filter(purchase_detail=purchase_detail_id).annotate(
            location_code=F('location__code'),
            packet_available=Exists(pack_type_detail)
        ).filter(packet_available=True, location__isnull=False).values("id", "location_code", "code")

    else:

        queryset = PackingTypeCode.objects.annotate(
            location_code=F('location__code'),
            packet_available=Exists(pack_type_detail),
            batch_no=F('purchase_detail__batch_no'),
            item_id=F('purchase_detail__item_id'),
            item_name=F('purchase_detail__item__name'),

        ).filter(packet_available=True, location__isnull=False).values("id", "location_code",
                                                                       "code", "batch_no",
                                                                       "purchase_detail", "item_id", "item_name")

    return queryset


def find_available_unserializable_pack(purchase_detail_id: int = None) -> PackingTypeCode.objects.none():

    sold_qty = SalePackingTypeCode.objects.filter(
        packing_type_code=OuterRef("pk"), ref_sale_packing_type_code__isnull=True
    ).values("packing_type_code").annotate(used_qty=Sum('qty')).values("used_qty")
    return_qty = SalePackingTypeCode.objects.filter(
        packing_type_code=OuterRef("pk"), ref_sale_packing_type_code__isnull=False
    ).values("packing_type_code").annotate(used_qty=Sum('qty')).values("used_qty")

    if purchase_detail_id is not None:

        queryset = PackingTypeCode.objects.filter(purchase_detail=purchase_detail_id).annotate(
            location_code=F('location__code'),
            remaining_qty=F('qty') - Coalesce(
                Subquery(sold_qty, output_field=DecimalField()), Decimal("0.00")
            ) + Coalesce(
                Subquery(return_qty, output_field=DecimalField()), Decimal("0.00")
            )
        ).filter(
            remaining_qty__gt=Decimal("0.00"), location__isnull=False
        ).values("id", "location_code", "code", "qty", "remaining_qty")

    else:

        queryset = PackingTypeCode.objects.annotate(
            location_code=F('location__code'),
            remaining_qty=F('qty') - Coalesce(
                Subquery(sold_qty, output_field=DecimalField()), Decimal("0.00")
            ) + Coalesce(
                Subquery(return_qty, output_field=DecimalField()), Decimal("0.00")
            ),
            batch_no=F('purchase_detail__batch_no'),
            item_id=F('purchase_detail__item_id'),
            item_name=F('purchase_detail__item__name')

        ).filter(remaining_qty__gt=Decimal("0.00"), location__isnull=False).values(
            "id", "location_code", "code", "batch_no",
            "purchase_detail", "item_id", "item_name", "qty", "remaining_qty"
        )

    return queryset


def find_available_serial_nos(pack_id: int = None) -> PackingTypeDetailCode.objects.none():
    pack_type_detail = PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        id=OuterRef("id"),
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0)

    if pack_id is not None:
        queryset = PackingTypeDetailCode.objects.filter(pack_type_code=pack_id).annotate(
            packet_available=Exists(pack_type_detail)
        ).filter(packet_available=True, pack_type_code__location__isnull=False).values("id", "code")
    else:
        queryset = PackingTypeDetailCode.objects.annotate(
            packet_available=Exists(pack_type_detail),
            batch_no=F('pack_type_code__purchase_detail__batch_no'),
            purchase_detail=F('pack_type_code__purchase_detail'),
            item_id=F('pack_type_code__purchase_detail__item_id'),
            item_name=F('pack_type_code__purchase_detail__item__name'),
        ).filter(packet_available=True, pack_type_code__location__isnull=False).values("id", "code", "pack_type_code",
                                                                                       "batch_no",
                                                                                       "purchase_detail", "item_id",
                                                                                       "item_name")

    return queryset


def find_available_serial_no(serial_no: str) -> bool:
    return PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        code=serial_no,
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0).exists()


def find_available_serial_no_id(serial_no: int) -> bool:
    return PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        id=serial_no,
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0).exists()


def find_available_pack_in_item(item_id: int = None) -> PackingTypeCode.objects.none():
    pack_type_detail = PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        pack_type_code=OuterRef("id"),
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0)

    queryset = PackingTypeCode.objects.filter(purchase_detail__item=item_id).annotate(
        location_code=F('location__code'),
        packet_available=Exists(pack_type_detail)
    ).filter(packet_available=True, location__isnull=False).values("id", "location_code", "code")

    return queryset


def find_available_item_serial_nos(item_id: int) -> bool:
    return PackingTypeDetailCode.objects.filter(
        assetlist__isnull=True,
        pack_type_code__purchase_detail__item=item_id,
        packingtypedetailcode__isnull=True
    ).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2
    ).filter(ref_count=0).values("id", "code", "pack_type_code")


def available_pack_qty_non_serializable(pack_type_code: int) -> dict:
    try:
        pack = PackingTypeCode.objects.filter(id=pack_type_code).values('id', 'qty').annotate(
            sold_qty=Coalesce(
                Sum('pack_type_code_of_sale__qty',
                    filter=Q(pack_type_code_of_sale__ref_sale_packing_type_code__isnull=True)), Decimal("0.00")
            ),
            return_qty=Coalesce(
                Sum('pack_type_code_of_sale__qty',
                           filter=Q(pack_type_code_of_sale__ref_sale_packing_type_code__isnull=False)), Decimal("0.00"))
        )
    except PackingTypeCode.DoesNotExist:
        raise Exception("packing type code does not exist")
    return pack[0]
