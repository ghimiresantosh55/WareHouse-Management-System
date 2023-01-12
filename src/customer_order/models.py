import nepali_datetime
from django.contrib.auth import get_user_model
from django.db import models
from simple_history import register

# log import
from log_app.models import LogBase
from src.core_app.models import CreateInfoModel, DiscountScheme
from src.custom_lib.functions.field_value_validation import gt_zero_validator
from src.customer.models import Customer
from src.item.models import Item, ItemCategory
from src.purchase.models import PurchaseDetail
from .managers import OrderDetailManager

User = get_user_model()


class OrderMaster(CreateInfoModel):
    STATUS_TYPE = (
        (1, "PENDING"),
        (2, "BILLED"),
        (3, "CANCELLED"),
        (4, "CHALAN")
    )
    order_no = models.CharField(
        max_length=20, unique=True, help_text="Order Id should be max. of 13 characters")
    status = models.PositiveIntegerField(choices=STATUS_TYPE,
                                         help_text="Where 1 = PENDING, 2 = BILLED,  3 = CANCELLED, 4 = CHALAN Default=1")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    discount_scheme = models.ForeignKey(
        DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount default=0.00")
    total_tax = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.0, help_text="Total tax default=0.00")
    sub_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.0, help_text="Sub total default=0.00")
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount")
    delivery_date_ad = models.DateField(
        max_length=10, help_text="Bill Date AD", blank=True, null=True)
    delivery_date_bs = models.CharField(
        max_length=10, help_text="Bill Date BS", blank=True)
    delivery_location = models.CharField(max_length=100, blank=True,
                                         help_text="Location should be max. of 100 characters")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total default=0.00")
    pick_verified = models.BooleanField(
        default=False, help_text="Customer order id picked from ware house")
    remarks = models.CharField(
        max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")
    by_batch = models.BooleanField(default=False, help_text="True if customer order is placed batch wise, False if "
                                                            "customer order is placed according to FIFO")
    verified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='customer_order_verified',
                                    null=True, blank=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="customer_order_approved",
                                    null=True, blank=True)
    CREDIT_TERM_CHOICES = (
        (15, "15 days"),
        (30, "30 days"),
        (45, "45 days"),
        (60, "60 days")
    )
    credit_term = models.PositiveIntegerField(null=True, blank=True, default=30, choices=CREDIT_TERM_CHOICES)

    def save(self, *args, **kwargs):
        if self.delivery_date_ad is not None:
            delivery_date_ad = nepali_datetime.date.from_datetime_date(
                self.delivery_date_ad)
            self.delivery_date_bs = delivery_date_ad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}:{self.order_no}"


register(OrderMaster, app="log_app", table_name="customer_order_ordermaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class OrderDetail(CreateInfoModel):
    order = models.ForeignKey(
        OrderMaster, on_delete=models.PROTECT, related_name='order_details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_category = models.ForeignKey(
        ItemCategory, null=True, blank=True, on_delete=models.PROTECT)
    qty = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[gt_zero_validator])
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                        help_text="purchase cost of order default=0.00")
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                    help_text="sale cost of order default=0.00")
    discountable = models.BooleanField(
        default=True, help_text="Check if item is discountable default=True")
    taxable = models.BooleanField(
        default=True, help_text="Check if item is discountable default=True")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                   help_text="Tax rate if item is taxable, default=0.00 max upto 100.00")
    tax_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                        help_text="Discount rate if item is discountable, default=0.00 and max upto "
                                                  "100.00")
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    gross_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    net_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, help_text='default = 0.00 ')
    cancelled = models.BooleanField(
        default=False, help_text='Cancelled default = False')
    picked = models.BooleanField(
        default=False, help_text="order picked from warehouse")
    purchase_detail = models.ForeignKey(
        PurchaseDetail, null=True, blank=True, on_delete=models.PROTECT)
    remarks = models.CharField(max_length=250, blank=True)
    picked_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="order_details_picked",
                                  null=True, blank=True)
    objects = OrderDetailManager()

    def __str__(self):
        return f"id: {self.id}:{self.item.name}"


register(OrderDetail, app="log_app", table_name="customer_order_orderdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
