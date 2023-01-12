from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs
from src.party_payment.models import PartyPayment

# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 7


# generate unique order_no for purchase_order_master
def get_receipt_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    count = PartyPayment.objects.filter(receipt_no__icontains=fiscal_year_code).count()
    max_id = str(count + 1)
    unique_id = "RE-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
    return unique_id
