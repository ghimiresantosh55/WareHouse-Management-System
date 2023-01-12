# queryset opertations
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import F
from django.db import connection
from src.purchase.models import PurchaseMaster
from src.supplier.models import Supplier
from django.db.models import Subquery


def get_purchase_credit_detail(supplier=None, purchase_master=None):
    # To calculate Total Credit amount, Paid Amount and Due amount of a bill supplier wise
    if supplier and purchase_master:
        bills = PurchaseMaster.objects.filter(pay_type=2, supplier=supplier, id=purchase_master) \
            .order_by('created_date_ad') \
            .values('supplier_id', 'purchase_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('supplier__name'),
            paid_amount=Coalesce(Sum('partyclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))
    elif supplier:
        bills = PurchaseMaster.objects.filter(pay_type=2, supplier=supplier) \
            .order_by('created_date_ad') \
            .values('supplier_id', 'purchase_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('supplier__name'),
            paid_amount=Coalesce(Sum('partyclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))
    elif purchase_master:
        bills = PurchaseMaster.objects.filter(pay_type=2, id=purchase_master) \
            .order_by('created_date_ad') \
            .values('supplier_id', 'purchase_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('supplier__name'),
            paid_amount=Coalesce(Sum('partyclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))
    else:
        bills = PurchaseMaster.objects.filter(pay_type=2) \
            .order_by('created_date_ad') \
            .values('supplier_id', 'purchase_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            date=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('supplier__name'),
            paid_amount=Coalesce(Sum('partyclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))


    return bills


# def get_supplier_credit_details(supplier=None):
#
#     query = supplier.objects.filter(PurchaseMaster__pay_type=2).values('id')\
#         .annotate(amount=Coalesce(Sum('PurchaseMaster__grand_total'), 0), supplier_name=F('name'),
#                   ).annotate(paid_amount=Coalesce(Sum('PurchaseMaster__creditclearancedetail__amount'), 0))
#
#     return query
