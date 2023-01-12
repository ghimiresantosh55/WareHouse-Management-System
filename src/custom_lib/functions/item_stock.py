from coreapi import Object
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from src.item.models import Item
from src.purchase.models import PurchaseDetail


def get_remaining_qty_of_item(item_id):
    try:
        return Item.objects.filter(active=True).values('id', 'name').annotate(
            remaining_qty=Coalesce(Sum(
            'purchasedetail__qty', 
            filter=Q(purchasedetail__purchase__purchase_type__in=[1,3,4])
            ), 0) 
            - Coalesce(Sum(
            'purchasedetail__qty', 
            filter=Q(purchasedetail__purchase__purchase_type__in=[2,3])
            ),0)
            - Coalesce(Sum(
                'saledetail__qty', 
                filter=Q(saledetail__sale_master__sale_type=1)
                ), 0) 
            + Coalesce(Sum(
                'saledetail__qty', 
                filter=Q(saledetail__sale_master__sale_type=2)
            ), 0)
        ).filter(remaining_qty__gt=0).get(id=item_id).remaining_qty
    except ObjectDoesNotExist:
        return 0



def get_remaining_purchase_details_of_item(item_id):
    qs  = PurchaseDetail.objects.filter(item_id).annotate(
            remaining_qty=Coalesce(Sum(
            'qty', 
            filter=Q(purchase__purchase_type__in=[1,3,4])
            ), 0) 
            - Coalesce(Sum(
            'qty', 
            filter=Q(purchase__purchase_type__in=[2,3])
            ),0)
            - Coalesce(Sum(
                'saledetail__qty', 
                filter=Q(saledetail__sale_master__sale_type=1)
                ), 0) 
            + Coalesce(Sum(
                'saledetail__qty', 
                filter=Q(saledetail__sale_master__sale_type=2)
            ), 0)
        ).filter(remaining_qty__gt=0)

    
def get_queryset_for_rem_qty_of_item():
    return Item.objects.filter(active=True).values('id', 'name').annotate(
            remaining_qty=Coalesce(Sum(
            'purchasedetail__qty', 
            filter=Q(purchasedetail__purchase__purchase_type__in=[1,3,4])
            ), 0) 
            - Coalesce(Sum(
            'purchasedetail__qty', 
            filter=Q(purchasedetail__purchase__purchase_type__in=[2,3])
            ),0)
            - Coalesce(Sum(
                'saledetail__qty', 
                filter=Q(saledetail__sale_master__sale_type=1)
                ), 0) 
            + Coalesce(Sum(
                'saledetail__qty', 
                filter=Q(saledetail__sale_master__sale_type=2)
            ), 0)
        ).filter(remaining_qty__gt=0)


        