from .models import QuotationMaster

# format order_no according to given digits
from ..custom_lib.functions.fiscal_year import get_fiscal_year_code_bs

QUOTATION_NO_LENGTH = 7


# generate unique order_no for order_master
def generate_quotation_no():
    cancel_count = QuotationMaster.objects.count()
    max_id = str(cancel_count + 1)
    fiscal_year_code = get_fiscal_year_code_bs()
    # generating of id like CO-77/78-0000000001 , CO-77/78-0000000002 ..
    unique_id = "QO-" + fiscal_year_code + "-" + max_id.zfill(QUOTATION_NO_LENGTH)
    return unique_id
