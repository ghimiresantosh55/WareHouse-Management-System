from rest_framework.exceptions import ValidationError

from .models import Account
from .models import VoucherMaster
from ..custom_lib.functions.fiscal_year import get_fiscal_year_code_bs

ORDER_NO_LENGTH = 7


def generate_voucher_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    cancel_count = VoucherMaster.objects.filter(voucher_no__icontains=fiscal_year_code).count()
    max_id = str(cancel_count + 1)

    # generating of id like CO-77/78-0000000001 , CO-77/78-0000000002 ..
    unique_id = "VC-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id


def generate_account_code(account_type):
    try:
        count = Account.objects.filter(type=account_type).order_by("id").last().id + 1
        count = str(count)
    except:
        count = str(1)
    if account_type == "ACCOUNT":
        unique_id = "AC-" + count.zfill(ORDER_NO_LENGTH)
    elif account_type == "CUSTOMER":
        unique_id = "CU-" + count.zfill(ORDER_NO_LENGTH)
    elif account_type == "SUPPLIER":
        unique_id = "SU-" + count.zfill(ORDER_NO_LENGTH)
    else:
        raise ValidationError({"account_type": f"account_type : {account_type} does not match"})

    return unique_id
