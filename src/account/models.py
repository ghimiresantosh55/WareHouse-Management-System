from decimal import Decimal

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from src.core_app.models import CreateInfoModel


# Create your models here.


class AccountGroup(MPTTModel, CreateInfoModel):
    name = models.CharField(max_length=250, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    def __str__(self):
        return f"{self.id} : {self.name}"


class Account(CreateInfoModel):
    ACCOUNT_TYPES = [
        ("ACCOUNT", "ACCOUNT"),
        ("CUSTOMER", "CUSTOMER"),
        ("SUPPLIER", "SUPPLIER")
    ]
    code = models.CharField(max_length=100)
    type = models.CharField(ACCOUNT_TYPES, default="ACCOUNT", max_length=100)
    name = models.CharField(max_length=250)
    group = models.ForeignKey(AccountGroup, on_delete=models.CASCADE, related_name="accounts")
    ref_id = models.PositiveIntegerField(default=0,
                                         help_text="reference to accounts in app like supplier, customer, user etc")
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.id} : {self.name}"


class VoucherMaster(CreateInfoModel):
    VOUCHER_TYPES = [
        ("JOURNAL", "Journal Voucher"),
        ("SALE", "Sale Voucher"),
        ("PURCHASE", "Purchase Voucher"),
        ("SUPPLIER", "Supplier Payment Voucher"),
        ("CUSTOMER", "Customer Payment Voucher"),
        ("PURCHASE-RETURN", "Purchase Return Voucher"),
        ("SALE-RETURN", "Sales Return Voucher"),
    ]
    type = models.CharField(choices=VOUCHER_TYPES, default="JOURNAL", max_length=100)
    voucher_no = models.CharField(max_length=250, unique=True)
    narration = models.CharField(max_length=250)
    reference = models.CharField(max_length=250, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class VoucherDetail(CreateInfoModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='vouchers')
    voucher_master = models.ForeignKey(VoucherMaster, on_delete=models.CASCADE, related_name="voucher_details")
    dr_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                    help_text="decimal max length 12 , decimal places 2")
    cr_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                    help_text="decimal max length 12 , decimal places 2")
    check_no = models.CharField(max_length=20, blank=True)
