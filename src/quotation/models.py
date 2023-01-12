from decimal import Decimal

import nepali_datetime
from django.db import models
from simple_history import register

# log import
from log_app.models import LogBase
from src.core_app.models import CreateInfoModel
from src.custom_lib.functions.field_value_validation import gt_zero_validator
from src.customer.models import Customer
from src.item.models import Item, ItemCategory


class QuotationMaster(CreateInfoModel):
    quotation_no = models.CharField(
        max_length=20, unique=True, help_text="Quotation Id should be max. of 13 characters")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    delivery_date_ad = models.DateField(
        max_length=10, help_text="Bill Date AD", blank=True, null=True)
    delivery_date_bs = models.CharField(
        max_length=10, help_text="Bill Date BS", blank=True)
    delivery_location = models.CharField(max_length=100, blank=True,
                                         help_text="Location should be max. of 100 characters")
    remarks = models.CharField(
        max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")

    cancelled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.delivery_date_ad is not None:
            delivery_date_ad = nepali_datetime.date.from_datetime_date(
                self.delivery_date_ad)
            self.delivery_date_bs = delivery_date_ad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}:{self.quotation_no}"


register(QuotationMaster, app="log_app", table_name="quotation_quotationmaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class QuotationDetail(CreateInfoModel):
    quotation = models.ForeignKey(
        QuotationMaster, on_delete=models.PROTECT, related_name='quotation_details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_category = models.ForeignKey(
        ItemCategory, null=True, blank=True, on_delete=models.PROTECT)
    qty = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[gt_zero_validator], default=Decimal("1.00"))
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"),
                                    help_text="sale cost of order default=0.00")
    remarks = models.CharField(max_length=50, blank=True)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"id: {self.id}:{self.item.name}"


register(QuotationDetail, app="log_app", table_name="quotation_quotationdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
