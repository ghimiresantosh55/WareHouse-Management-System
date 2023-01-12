from decimal import Decimal

from django.db.models import F, Subquery, DecimalField, OuterRef, Sum, Count
from django.db.models.functions import Coalesce

from src.chalan.models import ChalanDetail
from src.customer_order.models import OrderDetail
from src.ppb.models import TaskDetail
from src.purchase.models import PurchaseDetail
from src.sale.models import SaleDetail
from src.transfer.models import TransferDetail


def get_batch_stock() -> PurchaseDetail.objects.none():
    asset_count = PurchaseDetail.objects.filter(pk=OuterRef("pk"), ref_purchase_detail__isnull=True).annotate(
        asset_count=Count(
            'pu_pack_type_codes__pack_type_detail_codes__assetlist'
        )
    ).values('asset_count')
    purchase_return_qty = PurchaseDetail.objects.filter(ref_purchase_detail=OuterRef("pk")).values(
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
        purchase_detail=OuterRef("pk"), is_cancelled=False
    ).values("purchase_detail").annotate(
        task_qty=Sum("qty")
    ).values("task_qty")

    queryset = PurchaseDetail.objects.filter(
        ref_purchase_detail__isnull=True
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
        ) + Coalesce(
            Subquery(task_qty, output_field=DecimalField()), Decimal("0.00")
        )

    ).filter(remaining_qty__gt=0).values("id", "batch_no", "qty",
                                         "remaining_qty", "item", "purchase_cost")

    return queryset
