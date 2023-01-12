from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from simple_history import register

from log_app.models import LogBase
from src.core_app.models import CreateInfoModel, DiscountScheme, FiscalSessionAD, FiscalSessionBS
from src.item.models import Item, ItemCategory
from src.purchase.models import PurchaseDetail


class TransferOrderMaster(CreateInfoModel):
    transfer_order_no = models.CharField(max_length=20, unique=True,
                                         help_text="Transfer No should be of max 20 characters")
    branch = models.PositiveIntegerField()
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters and blank=True")
    cancelled = models.BooleanField(default=False)


class TransferOrderDetail(CreateInfoModel):
    transfer_order_master = models.ForeignKey(TransferOrderMaster, on_delete=models.CASCADE,
                                              related_name="transfer_order_details")
    item = models.ForeignKey(Item, default=False, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, default=False, on_delete=models.PROTECT)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                               help_text="cost can have max value upto=9999999999.99 and default=0.0")
    qty = models.DecimalField(max_digits=12, decimal_places=2,
                              help_text="Purchase quantity can have max value upto=9999999999.99 and min_value=0.0")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],
                                   help_text="pack quantity can't be negative")
    cancelled = models.BooleanField(default=False)
    ref_purchase_detail = models.ForeignKey(PurchaseDetail, related_name="transfer_order_purchase_details",
                                            on_delete=models.PROTECT)


class TransferMaster(CreateInfoModel):
    TRANSFER_TYPE = (
        (1, 'TRANSFER'),
        (2, 'RETURN'),
    )
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE)
    transfer_no = models.CharField(max_length=20, unique=True, help_text="Transfer No should be of max 20 characters")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Sub total can have max value upto=9999999999.99 and default=0.0")
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if applicable, default=0.0 and max_value upto=100.00")
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can have max value "
                                                              "upto=9999999999.99 and default=0.0")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount can have max value upto=9999999999.99 "
                                                         "and default=0.0")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount can have max value "
                                                             "upto=9999999999.99 and default=0.0")
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount can have max value upto=9999999999.99 and "
                                                   "default=0.0")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Total tax can have max value upto=9999999999.99 and default=0.0")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total can have max value upto=9999999999.99 and default=0.0")
    branch = models.PositiveIntegerField()
    branch_name = models.CharField(max_length=100, blank=True)
    fiscal_session_ad = models.ForeignKey(FiscalSessionAD, on_delete=models.PROTECT)
    fiscal_session_bs = models.ForeignKey(FiscalSessionBS, on_delete=models.PROTECT)
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters and blank=True")
    ref_transfer_master = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    ref_transfer_order_master = models.ForeignKey(TransferOrderMaster, on_delete=models.PROTECT, null=True, blank=True)
    return_dropped = models.BooleanField(default=True,
                                         help_text="True if items are dropped to locations after returning")
    active = models.BooleanField(default=True, help_text="By default active=True")
    is_transferred = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return "id {} : sale {}".format(self.id, self.transfer_no)


register(TransferMaster, app="log_app", table_name="transfer_transfermaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class TransferDetail(CreateInfoModel):
    transfer_master = models.ForeignKey(TransferMaster, on_delete=models.CASCADE, related_name='transfer_details')
    item = models.ForeignKey(Item, default=False, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, default=False, on_delete=models.PROTECT)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                               help_text="cost can have max value upto=9999999999.99 and default=0.0")
    qty = models.DecimalField(max_digits=12, decimal_places=2,
                              help_text="Purchase quantity can have max value upto=9999999999.99 and min_value=0.0")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],
                                   help_text="pack quantity can't be negative")

    taxable = models.BooleanField(default=True, help_text="Check if item is taxable")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                   help_text="Tax rate if item is taxable, max_value=100.00 and default=0.0")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                     help_text="Tax amount can have max value upto=9999999999.99 and default=0.0")
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if item is discountable, max_value=100.00 and "
                                                  "default=0.0")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                          help_text="Discount amount can have max value upto=9999999999.99 and "
                                                    "default=0.0")
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                       help_text="Gross amount can have max value upto=9999999999.99 and default=0.0")
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                     help_text="Net amount can have max value upto=9999999999.99 and default=0.0")
    ref_purchase_detail = models.ForeignKey(PurchaseDetail, related_name="transfer_purchase_details",
                                            on_delete=models.PROTECT)
    ref_transfer_detail = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    ref_transfer_order_detail = models.ForeignKey(TransferOrderDetail, on_delete=models.PROTECT, null=True, blank=True)
    cancelled = models.BooleanField(default=False)
    is_picked = models.BooleanField(default=False)

    def __str__(self):
        return "id {} : sale {}".format(self.id, self.transfer_master)


register(TransferDetail, app="log_app", table_name="transfer_transferdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
