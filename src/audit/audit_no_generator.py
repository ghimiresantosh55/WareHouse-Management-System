from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs

from .models import Audit, ItemAudit

# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 7


def generate_audit_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    cancel_count = Audit.objects.filter(audit_no__icontains=fiscal_year_code).count()
    max_id = str(cancel_count + 1)
    # generate id = PU-77/78-0000000001, PU-77/78-0000000002 ...
    #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
    unique_id = "AU-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
    return unique_id


def generate_item_audit_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    cancel_count = ItemAudit.objects.filter(audit_no__icontains=fiscal_year_code).count()
    max_id = str(cancel_count + 1)
    # generate id = PU-77/78-0000000001, PU-77/78-0000000002 ...
    #  zfill() method adds zeros (0) at the beginning of the string, until it reaches the specified length
    unique_id = "AU-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
    return unique_id
