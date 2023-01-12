# queryset opertations
from django.db.models import F
from django.db.models import Sum
from django.db.models.functions import Coalesce

from src.sale.models import SaleMaster


def get_sale_credit_detail(customer=None, sale_master=None):
    # To calculate Total Credit amount, Paid Amount and Due amount of a bill customer wise
    if customer and sale_master:
        bills = SaleMaster.objects.filter(pay_type=2, customer=customer, id=sale_master) \
            .order_by('created_date_ad') \
            .values('customer_id', 'sale_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('customer__first_name'),
            paid_amount=Coalesce(Sum('creditclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))
    elif customer:
        bills = SaleMaster.objects.filter(pay_type=2, customer=customer) \
            .order_by('created_date_ad') \
            .values('customer_id', 'sale_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('customer__first_name'),
            paid_amount=Coalesce(Sum('creditclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))
    elif sale_master:
        bills = SaleMaster.objects.filter(pay_type=2, id=sale_master) \
            .order_by('created_date_ad') \
            .values('customer_id', 'sale_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('customer__first_name'),
            paid_amount=Coalesce(Sum('creditclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))
    else:
        bills = SaleMaster.objects.filter(pay_type=2) \
            .order_by('created_date_ad') \
            .values('customer_id', 'sale_no') \
            .annotate(
            total_amount=F('grand_total'),
            sale_id=F('id'),
            created_date_ad=F('created_date_ad'),
            date=F('created_date_ad'),
            created_date_bs=F('created_date_bs'),
            created_by_user_name=F('created_by__user_name'),
            created_by=F('created_by'),
            remarks=F('remarks'),
            name=F('customer__first_name'),
            paid_amount=Coalesce(Sum('creditclearance__total_amount'), 0)
        ) \
            .annotate(due_amount=F('grand_total') - F('paid_amount'))

    return bills

# def get_customer_credit_details(customer=None):
#
#     query = Customer.objects.filter(salemaster__pay_type=2).values('id')\
#         .annotate(amount=Coalesce(Sum('salemaster__grand_total'), 0), customer_name=F('name'),
#                   ).annotate(paid_amount=Coalesce(Sum('salemaster__creditclearancedetail__amount'), 0))
#
#     return query
