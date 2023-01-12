from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs
from .models import DepartmentTransferMaster

# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 7
fiscal_year_code = get_fiscal_year_code_bs()


# generate unique order_no for purchase_order_master
def generate_department_transfer_no(transfer_type):
    if transfer_type == 1:
        count = DepartmentTransferMaster.objects.filter(
            transfer_type=transfer_type,
            transfer_no__icontains=fiscal_year_code).count()
        max_id = str(count + 1)
        unique_id = "DTF-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id
    elif transfer_type == 2:
        count = DepartmentTransferMaster.objects.filter(
            transfer_type=transfer_type,
            transfer_no__icontains=fiscal_year_code).count()
        max_id = str(count + 1)
        unique_id = "DTR-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id


