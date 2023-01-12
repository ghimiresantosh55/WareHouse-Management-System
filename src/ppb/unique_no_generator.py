from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs
from src.ppb.models import PPBMain, TaskMain


def generate_ppb_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    ppb_count = PPBMain.objects.filter(ppb_no__icontains=fiscal_year_code).count()
    max_id = str(ppb_count + 1)

    return "PPB-" + fiscal_year_code + "-" + max_id.zfill(7)


def generate_task_no():
    fiscal_year_code = get_fiscal_year_code_bs()
    task_count = TaskMain.objects.filter(task_no__icontains=fiscal_year_code).count()
    max_id = str(task_count + 1)

    return "TK-" + fiscal_year_code + "-" + max_id.zfill(7)
