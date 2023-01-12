from src.credit_management.models import CreditClearance
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs

# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 7


# generate unique order_no for purchase_order_master
def get_receipt_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    # auto-increment of id for CreditClearance
    # counting total number of list(i.e. row) in CreditClearance
    count = CreditClearance.objects.filter(receipt_no__icontains=fiscal_year_code).count()
    max_id = str(count + 1)
    # gettting fiscal year

    # RE-77/78-0000000001, RE-77/78-0000000002, RE-77/78-0000000003 and so on...
    unique_id = "RE-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
    return unique_id
