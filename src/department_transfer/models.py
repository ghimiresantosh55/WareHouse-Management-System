from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from src.core_app.models import CreateInfoModel
from src.department.models import Department
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail
from src.purchase.models import PurchaseMaster, PurchaseDetail

User = get_user_model()


# Create your models here.
class DepartmentTransferMaster(CreateInfoModel):
    DEPARTMENT_TRANSFER_TYPE = (
        (1, "TRANSFER"),
        (2, "RETURN"),
    )

    transfer_no = models.CharField(max_length=20, unique=True,
                                   help_text="Purchase no. should be max. of 10 characters")
    transfer_type = models.PositiveIntegerField(choices=DEPARTMENT_TRANSFER_TYPE,
                                                help_text="Purchase type like 1= transfer, 2 = Return")

    from_department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True,
                                        related_name="department_transfer_from")
    to_department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True,
                                      related_name="department_transfer_to")

    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total can be max upto 9999999999.99")
    bill_no = models.CharField(max_length=20, help_text="Bill no.", blank=True)

    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks can be max. of 100 characters")
    ref_department_transfer_master = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="department_transfer_master_approved",
                                    null=True, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="department_transfer_master_received",
                                    null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    is_picked = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    def __str__(self):
        return f"{self.id} : {self.transfer_type} : {self.transfer_no}"


class DepartmentTransferDetail(CreateInfoModel):
    department_transfer_master = models.ForeignKey(DepartmentTransferMaster, related_name="department_transfer_details",
                                                   on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                        help_text="purchase_cost can be max value upto 9999999999.99 and default=0.0")
    qty = models.DecimalField(max_digits=12, decimal_places=2,
                              help_text="Purchase quantity can be max value upto 9999999999.99 and default=0.0")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    packing_type = models.ForeignKey(PackingType, on_delete=models.PROTECT)
    packing_type_detail = models.ForeignKey(PackingTypeDetail, on_delete=models.PROTECT)
    expirable = models.BooleanField(default=False, help_text="Check if item is Expirable, default=False")
    expiry_date_ad = models.DateField(max_length=10, help_text="Expiry Date AD", null=True, blank=True)
    expiry_date_bs = models.CharField(max_length=10, help_text="Expiry Date BS", blank=True)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                     help_text="Net amount can be max upto 9999999999.99 and default=0.0")
    ref_department_transfer_detail = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    ref_purchase_detail = models.ForeignKey(PurchaseDetail, related_name='department_transfer_detail',
                                            on_delete=models.PROTECT,
                                            blank=True, null=True)
    is_cancelled = models.BooleanField(default=False)
    picked_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="department_transfer_details_picked",
                                  null=True, blank=True)
    is_picked = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
