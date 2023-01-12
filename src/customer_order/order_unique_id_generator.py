from src.advance_deposit.models import AdvancedDeposit
from .models import OrderMaster
# format order_no according to given digits
from ..custom_lib.functions.fiscal_year import get_fiscal_year_code_bs

ORDER_NO_LENGTH = 7


# generate unique order_no for order_master
def generate_customer_order_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    cancel_count = OrderMaster.objects.filter(order_no__icontains=fiscal_year_code).count()
    max_id = str(cancel_count + 1)

    # generating of id like CO-77/78-0000000001 , CO-77/78-0000000002 ..
    unique_id = "CO-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id


def generate_advanced_deposit_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    deposit_count = AdvancedDeposit.objects.filter(deposit_no__icontains=fiscal_year_code).count()
    max_id = str(deposit_count + 1)

    # generating of id like AD-77/78-0000000001 , AD-77/78-0000000002 ..
    unique_id = "AD-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id
