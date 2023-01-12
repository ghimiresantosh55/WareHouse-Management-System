from django.db.models import Sum, Q, F

from src.customer_order.models import OrderMaster


def fix_customer_order_total_amounts():
    error_customer_order_amounts = OrderMaster.objects.exclude(status=3).values('id', 'sub_total', 'grand_total',
                                                                                'order_no').annotate(
        total_gross_amount=Sum('order_details__gross_amount', filter=Q(order_details__cancelled=False)),
        total_net_amount=Sum('order_details__net_amount', filter=Q(order_details__cancelled=False)),
    ).exclude(Q(sub_total=F('total_gross_amount')) & Q(grand_total=F('total_net_amount')))
    for error_customer_order_amount in error_customer_order_amounts:
        order_master = OrderMaster.objects.get(id=error_customer_order_amount['id'])
        order_master.sub_total = error_customer_order_amount['total_gross_amount']
        order_master.grand_total = error_customer_order_amount['total_net_amount']
        order_master.save()
