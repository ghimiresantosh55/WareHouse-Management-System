from decimal import Decimal

from django.db.models import OuterRef, Subquery, Sum, Count, DecimalField, Q, Max
from django.db.models.functions import Coalesce

from src.item.models import Item
from src.ppb.models import TaskDetail
from src.purchase.models import PurchaseDetail


def get_remaining_sold_purchased_item(item_id: int = None) -> Item:
    transfer_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        transfer_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=1,
                                                         transferdetail__cancelled=False))
    ).values("transfer_qty")
    transfer_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        transfer_return_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=2,
                                                                transferdetail__cancelled=False))
    ).values("transfer_return_qty")
    asset_count = Item.objects.filter(pk=OuterRef("pk")).annotate(
        asset_count=Count(
            'purchasedetail__pu_pack_type_codes__pack_type_detail_codes__assetlist',
            filter=Q(purchasedetail__ref_purchase_detail__isnull=True)
        )
    ).values('asset_count')
    purchase_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        purchase_qty=Sum(
            'purchasedetail__qty',
            filter=Q(purchasedetail__purchase__purchase_type__in=[1, 3, 4])
            # & Q(purchasedetail__pu_pack_type_codes__location__isnull=False)
        )
    ).values('purchase_qty')

    purchase_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        purchase_return_qty=Sum(
            'purchasedetail__qty',
            filter=Q(purchasedetail__purchase__purchase_type__in=[2, 5])
        )
    ).values('purchase_return_qty')

    sale_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        sale_qty=Sum(
            'saledetail__qty',
            filter=Q(saledetail__sale_master__sale_type=1)
        )
    ).values('sale_qty')
    sale_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        sale_return_qty=Sum(
            'saledetail__qty',
            filter=Q(saledetail__sale_master__sale_type=2, saledetail__sale_master__return_dropped=True)
        )
    ).values('sale_return_qty')

    chalan_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        chalan_qty=Sum(
            'chalandetail__qty',
            filter=Q(chalandetail__chalan_master__status=1)
        )
    ).values('chalan_qty')

    chalan_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        chalan_return_qty=Sum(
            'chalandetail__qty',
            filter=Q(chalandetail__chalan_master__status=3, chalandetail__chalan_master__return_dropped=True)
        )
    ).values('chalan_return_qty')

    pending_customer_order_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        pending_customer_order_qty=Sum(
            'orderdetail__qty',
            filter=Q(orderdetail__cancelled=False, orderdetail__order__status=1)
        )
    ).values('pending_customer_order_qty')

    task_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        task_qty=Sum(
            'taskdetail__qty', filter=Q(taskdetail__is_cancelled=False)
        )
    ).values("task_qty")

    task_output_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
        task_output_qty=Sum(
            'taskoutput_qty'
        )
    ).values("task_output_qty")

    highest_sale_cost = PurchaseDetail.objects.filter(item=OuterRef("id")).values('item').annotate(
        highest_sale_cost=Max("sale_cost")
    ).values("highest_sale_cost")

    queryset = Item.objects.filter(active=True).annotate(
        remaining_qty=Coalesce(
            Subquery(purchase_qty, output_field=DecimalField()), Decimal("0.00")
        ) - Coalesce(
            Subquery(purchase_return_qty, output_field=DecimalField()), Decimal("0.00")
        ) - Coalesce(
            Subquery(sale_qty, output_field=DecimalField()), Decimal("0.00")
        ) + Coalesce(
            Subquery(sale_return_qty, output_field=DecimalField()), Decimal("0.00")
        ) - Coalesce(
            Subquery(pending_customer_order_qty, output_field=DecimalField()), Decimal("0.00")
        ) - Subquery(
            asset_count, output_field=DecimalField()
        ) - Coalesce(
            Subquery(chalan_qty, output_field=DecimalField()), Decimal("0.00")
        ) + Coalesce(
            Subquery(chalan_return_qty, output_field=DecimalField()), Decimal("0.00")
        ) - Coalesce(
            Subquery(transfer_qty, output_field=DecimalField()), Decimal("0.00")
        ) + Coalesce(
            Subquery(transfer_return_qty, output_field=DecimalField()), Decimal("0.00")
        ) - Coalesce(
            Subquery(task_qty, output_field=DecimalField()), Decimal("0.00")
        ) + Coalesce(
            Subquery(task_output_qty, output_field=DecimalField()), Decimal("0.00")
        ),
        item_highest_cost=Subquery(highest_sale_cost, output_field=DecimalField())
    ).values(
        'id', 'purchase_cost', 'item_highest_cost', 'name', 'discountable',
        'taxable', 'tax_rate', 'code', 'item_category',
        'remaining_qty', 'sale_cost'
    )
    if item_id:
        return queryset.get(id=item_id)

    return queryset.filter(remaining_qty__gt=0)
