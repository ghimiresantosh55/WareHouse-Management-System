from .models import ChalanMaster

# format order_no according to given digits
from ..custom_lib.functions.fiscal_year import get_fiscal_year_code_bs

ORDER_NO_LENGTH = 7


# generate unique order_no for order_master
def generate_chalan_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    chalan_count = ChalanMaster.objects.filter(status__in=[1, 2], chalan_no__icontains=fiscal_year_code).count()
    max_id = str(chalan_count + 1)
    # generating of id like CO-77/78-0000000001 , CO-77/78-0000000002 ..
    unique_id = "CH-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id


def generate_chalan_return_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    chalan_count = ChalanMaster.objects.filter(status=3, chalan_no__icontains=fiscal_year_code).count()
    max_id = str(chalan_count + 1)

    # generating of id like CO-77/78-0000000001 , CO-77/78-0000000002 ..
    unique_id = "CR-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id
