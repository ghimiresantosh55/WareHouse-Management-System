from src.advance_deposit.models import AdvancedDeposit

# format order_no according to given digits
from ..custom_lib.functions.fiscal_year import get_fiscal_year_code_bs

ORDER_NO_LENGTH = 7


def generate_advanced_deposit_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    deposit_count = AdvancedDeposit.objects.filter(deposit_no__icontains=fiscal_year_code).count()
    max_id = str(deposit_count + 1)
    unique_id = "AD-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id
