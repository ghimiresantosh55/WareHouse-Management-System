from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs
from .models import SaleMaster

# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 7
fiscal_year_code = get_fiscal_year_code_bs()


# generate unique order_no for purchase_order_master
def generate_sale_no(sale_type):
    if sale_type == 1:
        count = SaleMaster.objects.filter(sale_type=sale_type, sale_no__icontains=fiscal_year_code).count()
        max_id = str(count + 1)
        unique_id = "SA-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id
    elif sale_type == 2:
        count = SaleMaster.objects.filter(sale_type=sale_type, sale_no__icontains=fiscal_year_code).count()
        max_id = str(count + 1)
        unique_id = "SR-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id


00
