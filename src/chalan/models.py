from django.db import models
from simple_history import register

# log import
from log_app.models import LogBase
from src.core_app.models import AdditionalChargeType, CreateInfoModel, DiscountScheme, PaymentMode
from src.custom_lib.functions.field_value_validation import gt_zero_validator
from src.customer.models import Customer
from src.customer_order.models import OrderDetail, OrderMaster
from src.item.models import Item, ItemCategory
from src.purchase.models import PurchaseDetail


class ChalanMaster(CreateInfoModel):
    STATUS_TYPE = (
        (1, "CHALAN"),
        (2, "BILLED"),
        (3, "RETURNED")
    )
    chalan_no = models.CharField(max_length=20, unique=True, help_text="Chalan No should be max. of 20 characters")
    status = models.PositiveIntegerField(choices=STATUS_TYPE,
                                         help_text="Where 1 = CHALAN, 2 = BILLED,  3 = RETURNED, Default=1")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if applicable, default=0.0 and max_value upto=100.00")
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount default=0.00")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, help_text="Total tax default=0.00")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, help_text="Sub total default=0.00")
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total default=0.00")
    ref_order_master = models.ForeignKey(OrderMaster, null=True, blank=True, on_delete=models.PROTECT)
    remarks = models.CharField(max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")
    return_dropped = models.BooleanField(default=True,
                                         help_text="True if items are dropped to locations after returning")
    ref_chalan_master = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.id}:{self.chalan_no}"


register(ChalanMaster, app="log_app", table_name="chalan_chalanmaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class ChalanDetail(CreateInfoModel):
    chalan_master = models.ForeignKey(ChalanMaster, on_delete=models.PROTECT, related_name='chalan_details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, null=True, blank=True, on_delete=models.PROTECT)
    qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[gt_zero_validator])
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                    help_text="sale cost of order default=0.00")
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable default=True")
    taxable = models.BooleanField(default=True, help_text="Check if item is discountable default=True")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                   help_text="Tax rate if item is taxable, default=0.00 max upto 100.00")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                        help_text="Discount rate if item is discountable, default=0.00 and max upto "
                                                  "100.00")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    ref_purchase_detail = models.ForeignKey(PurchaseDetail, null=True, blank=True, on_delete=models.PROTECT)
    ref_order_detail = models.ForeignKey(OrderDetail, null=True, blank=True, on_delete=models.PROTECT)
    remarks = models.CharField(max_length=50, blank=True)
    ref_chalan_detail = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"id: {self.id}:{self.item.name}"


register(ChalanDetail, app="log_app", table_name="chalan_chalandetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
