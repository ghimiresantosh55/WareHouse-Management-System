import nepali_datetime
from django.db import models
# log import
from log_app.models import LogBase
from simple_history import register
from src.core_app.models import CreateInfoModel, DiscountScheme, PaymentMode
from src.customer_order.models import OrderMaster
from src.sale.models import SaleMaster

# Create your models here.
"""____________________________________________Models for Advanced Payment__________________________________________"""


class AdvancedDeposit(CreateInfoModel):
    DEPOSIT_TYPE = (
        (1, "DEPOSIT"),
        (2, "DEPOSIT-RETURN"),
    )

    order_master = models.ForeignKey(OrderMaster, on_delete=models.PROTECT, related_name="advanced_deposits")
    advanced_deposit_type = models.PositiveIntegerField(choices=DEPOSIT_TYPE,
                                                        help_text="Advanced Deposit type like 1= Deposit, 2 = Return")
    # sale_master is updated when order is converted into bill else it remains null/blank
    sale_master = models.ForeignKey(SaleMaster, on_delete=models.PROTECT, related_name="sale_master",
                                    blank=True, null=True)
    # DE for deposit, DR for deposit return
    deposit_no = models.CharField(max_length=20, help_text="max deposit_no should not be greater than 13")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum value upto 99999999999.99" )
    remarks = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.id}"


register(AdvancedDeposit, app="log_app", table_name="advance_deposit_advanceddeposit_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AdvancedDepositPaymentDetail(CreateInfoModel):
    advanced_deposit = models.ForeignKey(AdvancedDeposit, on_delete=models.PROTECT, related_name="advanced_deposit_payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum value upto 99999999999.99")
    remarks = models.CharField(max_length=50, blank=True, help_text="remarks can be upto 50 characters")

    def __str__(self):
        return f"{self.id}"


register(AdvancedDepositPaymentDetail, app="log_app", table_name="advance_deposit_advanceddepositpaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
