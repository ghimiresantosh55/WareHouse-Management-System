from decimal import Decimal

from django.db.models import Sum, OuterRef, Q, Count, Max, Subquery, DecimalField, F
from django.db.models.functions import Coalesce

from ...asset.models import AssetList
from ...chalan.models import ChalanDetail
from ...customer_order.models import OrderDetail
from ...item.models import Item
from ...ppb.models import TaskDetail
from ...purchase.models import PurchaseDetail
from ...sale.models import SaleDetail
from ...transfer.models import TransferDetail


def stock_by_department_queryset(department_id):
    """
        Old query
    """
    # purchase_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     purchase_qty=Sum(
    #         'purchasedetail__qty',
    #         filter=Q(purchasedetail__purchase__purchase_type__in=[1, 3, 4])
    #         # & Q(purchasedetail__pu_pack_type_codes__location__isnull=False)
    #     )
    # ).values('purchase_qty')

    purchase_qty = PurchaseDetail.objects.filter(
        purchase__department=department_id, item=OuterRef("pk"), ref_purchase_detail__isnull=True
    ).values("item").annotate(
        purchase_qty=Sum('qty')
    ).values("purchase_qty")

    """
    Old query
    """
    # purchase_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     purchase_return_qty=Sum(
    #         'purchasedetail__qty',
    #         filter=Q(purchasedetail__purchase__purchase_type__in=[2, 5])
    #     )
    # ).values('purchase_return_qty')

    purchase_return_qty = PurchaseDetail.objects.filter(
        purchase__department=department_id, item=OuterRef("pk"), ref_purchase_detail__isnull=False
    ).values("item").annotate(
        purchase_return_qty=Sum('qty')
    ).values("purchase_return_qty")

    """
    Old Query
    """
    # transfer_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     transfer_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=1,
    #                                                      transferdetail__cancelled=False))
    # ).values("transfer_qty")

    transfer_qty = TransferDetail.objects.filter(
        ref_purchase_detail__purchase__department=department_id, item=OuterRef("pk"), ref_transfer_detail=0,
        cancelled=False
    ).values("item").annotate(transfer_qty=Sum('qty')).values("transfer_qty")

    """
    Old Query
    """
    # transfer_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     transfer_return_qty=Sum('transferdetail__qty', filter=Q(transferdetail__transfer_master__transfer_type=2,
    #                                                             transferdetail__cancelled=False))
    # ).values("transfer_return_qty")

    transfer_return_qty = TransferDetail.objects.filter(
        ref_purchase_detail__purchase__department=department_id, item=OuterRef("pk"), ref_transfer_detail__gt=0,
        cancelled=False
    ).values("item").annotate(transfer_return_qty=Sum('qty')).values("transfer_return_qty")

    asset_count = Item.objects.filter(pk=OuterRef("pk")).annotate(
        asset_count=Count(
            'purchasedetail__pu_pack_type_codes__pack_type_detail_codes__assetlist',
            filter=Q(purchasedetail__ref_purchase_detail__isnull=True)
        )
    ).values('asset_count')

    """
    Old Query
    """
    # sale_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     sale_qty=Sum(
    #         'saledetail__qty',
    #         filter=Q(saledetail__sale_master__sale_type=1)
    #     )
    # ).values('sale_qty')

    sale_qty = SaleDetail.objects.filter(
        ref_purchase_detail__purchase__department=department_id, item=OuterRef("pk"),
        ref_sale_detail__isnull=True
    ).values("item").annotate(sale_qty=Sum("qty")).values("sale_qty")

    """
       Old Query
    """
    # sale_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     sale_return_qty=Sum(
    #         'saledetail__qty',
    #         filter=Q(saledetail__sale_master__sale_type=2, saledetail__sale_master__return_dropped=True)
    #     )
    # ).values('sale_return_qty')

    sale_return_qty = SaleDetail.objects.filter(
        ref_purchase_detail__purchase__department=department_id, item=OuterRef("pk"),
        ref_sale_detail__isnull=True,
        sale_master__return_dropped=True
    ).values("item").annotate(sale_return_qty=Sum("qty")).values("sale_return_qty")

    """
        Old Query
    """
    # chalan_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     chalan_qty=Sum(
    #         'chalandetail__qty',
    #         filter=Q(chalandetail__chalan_master__status=1)
    #     )
    # ).values('chalan_qty')

    chalan_qty = ChalanDetail.objects.filter(
        ref_purchase_detail__purchase__department=department_id, item=OuterRef("pk"), chalan_master__status=1
    ).values("item").annotate(chalan_qty=Sum("qty")).values("chalan_qty")

    """
    Old Query
    """
    # chalan_return_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     chalan_return_qty=Sum(
    #         'chalandetail__qty',
    #         filter=Q(chalandetail__chalan_master__status=3,
    #                  chalandetail__chalan_master__return_dropped=True)
    #     )
    # ).values('chalan_return_qty')

    chalan_return_qty = ChalanDetail.objects.filter(
        ref_purchase_detail__purchase__department=department_id,
        item=OuterRef("pk"), chalan_master__status=1,
        chalan_master__return_dropped=True
    ).values("item").annotate(chalan_return_qty=Sum("qty")).values("chalan_return_qty")

    """
    Old Query
    """

    # pending_customer_order_qty = Item.objects.filter(pk=OuterRef("pk")).annotate(
    #     pending_customer_order_qty=Sum(
    #         'orderdetail__qty',
    #         filter=Q(orderdetail__cancelled=False, orderdetail__order__status=1)
    #     )
    # ).values('pending_customer_order_qty')

    pending_customer_order_qty = OrderDetail.objects.filter(
        purchase_detail__purchase__department=department_id, item=OuterRef("pk"),
        cancelled=False, order__status=1
    ).values("item").annotate(pending_customer_order_qty=Sum("qty")).values("pending_customer_order_qty")

    # highest_sale_cost = PurchaseDetail.objects.filter(item=OuterRef("id")).values('item').annotate(
    #     highest_sale_cost=Max("sale_cost")
    # ).values("highest_sale_cost")

    task_qty = TaskDetail.objects.filter(
        purchase_detail__purchase__department=department_id, item=OuterRef("pk"), is_cancelled=False
    ).values("item").annotate(task_qty_count=Sum("qty")).values("task_qty_count")

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
        ),
        unit_name=F('unit__name')
    ).values(
        'id', 'purchase_cost', 'name', 'discountable',
        'taxable', 'tax_rate', 'code', 'item_category',
        'remaining_qty', 'sale_cost', 'unit_name'
    )

    return queryset


def get_department_batch_stock(department_id) -> PurchaseDetail.objects.none():
    asset_count = PurchaseDetail.objects.filter(
        pk=OuterRef("pk"), ref_purchase_detail__isnull=True
    ).annotate(
        asset_count=Count(
            'pu_pack_type_codes__pack_type_detail_codes__assetlist'
        )
    ).values('asset_count')
    purchase_return_qty = PurchaseDetail.objects.filter(
        ref_purchase_detail=OuterRef("pk"),
    ).values(
        "ref_purchase_detail"
    ).annotate(
        purchase_return_qty=Sum(
            'qty',
            output_field=DecimalField()
        )
    ).values('purchase_return_qty')

    sale_qty = SaleDetail.objects.filter(ref_purchase_detail=OuterRef("pk"), sale_master__sale_type=1).values(
        "ref_purchase_detail").annotate(
        sale_qty=Sum(
            'qty'
        )
    ).values('sale_qty')

    transfer_qty = TransferDetail.objects.filter(
        ref_purchase_detail=OuterRef("pk"), transfer_master__transfer_type=1, cancelled=False
    ).values("ref_purchase_detail").annotate(
        transfer_qty=Sum('qty')
    ).values("transfer_qty")
    transfer_return_qty = TransferDetail.objects.filter(
        ref_purchase_detail=OuterRef("pk"), transfer_master__transfer_type=2, cancelled=False
    ).values("ref_purchase_detail").annotate(
        transfer_return_qty=Sum('qty')
    ).values("transfer_return_qty")

    sale_return_qty = SaleDetail.objects.filter(
        ref_purchase_detail=OuterRef("pk"), sale_master__sale_type=2, sale_master__return_dropped=True).annotate(
        sale_return_qty=Sum(
            'qty'
        )
    ).values('sale_return_qty')

    chalan_qty = ChalanDetail.objects.filter(
        ref_purchase_detail=OuterRef("pk"), chalan_master__status=1
    ).values("ref_purchase_detail").annotate(
        chalan_qty=Sum(
            'qty'
        )
    ).values('chalan_qty')

    chalan_return_qty = ChalanDetail.objects.filter(
        ref_purchase_detail=OuterRef("pk"), chalan_master__status=3, chalan_master__return_dropped=True
    ).values("ref_purchase_detail").annotate(
        chalan_return_qty=Sum(
            'qty'
        )
    ).values('chalan_return_qty')

    pending_customer_order_qty = OrderDetail.objects.filter(
        purchase_detail=OuterRef("pk"), order__status=1, cancelled=False
    ).values("purchase_detail").annotate(
        pending_customer_order_qty=Sum(
            'qty'
        )
    ).values('pending_customer_order_qty')

    task_qty = TaskDetail.objects.filter(
        purchase_detail=OuterRef("pk")
    ).values("purchase_detail").annotate(
        task_qty=Sum("qty")
    ).values("task_qty")

    queryset = PurchaseDetail.objects.filter(
        ref_purchase_detail__isnull=True, purchase__department=department_id
    ).annotate(
        remaining_qty=
        F('qty')
        - Coalesce(
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
        ),
        department=F("purchase__department")
    ).filter(remaining_qty__gt=0).values("id", "batch_no", "qty",
                                         "remaining_qty", "item", "purchase_cost", "department")

    return queryset
