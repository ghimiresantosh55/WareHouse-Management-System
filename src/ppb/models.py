from django.db import models
from django.utils.translation import ugettext_lazy as _

from src.core_app.models import CreateInfoModel
from src.department.models import Department
from src.item.models import Item, Unit, PackingType, PackingTypeDetail
from src.purchase.models import PurchaseDetail
from django.contrib.auth import get_user_model

User = get_user_model()


class PPBMain(CreateInfoModel):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the PPB item, can be of max 100 characters")
    ppb_no = models.CharField(max_length=20, unique=True, help_text="PPB no for the item, can be of max 15 characters")
    active = models.BooleanField(default=True)
    output_item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="output_item_ppb")
    remarks = models.CharField(max_length=255, blank=True, null=True, help_text="remarks for ppb main")

    class Meta:
        verbose_name = _('PPBMain')
        verbose_name_plural = _('PPBMains')

    def __str__(self):
        return f"{self.id} : {self.ppb_no}"

    @property
    def get_ppb_name(self):
        return self.name


class PPBDetail(CreateInfoModel):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="item_ppb")
    qty = models.DecimalField(decimal_places=2, max_digits=12)
    ppb_main = models.ForeignKey(PPBMain, on_delete=models.PROTECT, related_name="ppb_details")
    active = models.BooleanField(default=True, help_text="PPB Detail active status is default to True")

    def __str__(self):
        return f"{self.id} : {self.item}"


class TaskMain(CreateInfoModel):
    ppb_main = models.ForeignKey(PPBMain, on_delete=models.PROTECT, related_name="ppb_task")
    expected_output_qty = models.DecimalField(decimal_places=2, max_digits=12)
    task_no = models.CharField(max_length=20, unique=True)
    output_item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="output_item_task")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="task_department")
    remarks = models.CharField(max_length=255, blank=True, null=True, help_text="remarks for task main")
    is_approved = models.BooleanField(default=False, help_text="Approve Task by Permitted User")
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="task_main_approved")
    is_cancelled = models.BooleanField(default=False, help_text="Cancel entire task")

    @property
    def get_department_name(self):
        return self.department.name

    def __str__(self):
        return f"{self.id} : {self.task_no}"


class TaskDetail(CreateInfoModel):
    task_main = models.ForeignKey(TaskMain, on_delete=models.PROTECT, related_name="task_details")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="task_details_item")
    qty = models.DecimalField(decimal_places=2, max_digits=12)
    ppb_detail = models.ForeignKey(PPBDetail, on_delete=models.PROTECT, related_name="task_details_ppb")
    purchase_detail = models.ForeignKey(PurchaseDetail, on_delete=models.PROTECT, related_name="task_detail_purchase")
    is_cancelled = models.BooleanField(default=False, help_text="Cancel a task detail")
    picked = models.BooleanField(default=False, help_text="picked boolean for task detail, defaults to false")
    picked_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="task_details_picked")

    def __str__(self):
        return f"{self.id} : {self.item} : {self.task_main.task_no}"


class TaskOutput(CreateInfoModel):
    task_main = models.ForeignKey(TaskMain, on_delete=models.PROTECT, related_name="task_output")
    qty = models.DecimalField(decimal_places=2, max_digits=12)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="task_output_item")
    packing_type = models.ForeignKey(PackingType, on_delete=models.PROTECT)
    packing_type_detail = models.ForeignKey(PackingTypeDetail, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.id}"
