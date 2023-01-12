from django.db import models
from simple_history import register

# log inport
from log_app.models import LogBase
from src.core_app.models import CreateInfoModel, PaymentMode
from src.sale.models import SaleMaster


class CreditClearance(CreateInfoModel):
    PAYMENT_TYPE = (
        (1, "PAYMENT"),
        (2, "REFUND"),
    )

    sale_master = models.ForeignKey(SaleMaster, on_delete=models.PROTECT, related_name="credit_clearances")
    payment_type = models.PositiveIntegerField(choices=PAYMENT_TYPE, default=1,
                                               help_text="Where 1 = PAYMENT, 2 = REFUND, default=1")
    receipt_no = models.CharField(max_length=20, help_text="receipt_no can be upto 20 characters")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                       help_text="max_value upto 9999999999.99, min_value=0.0")
    remarks = models.CharField(max_length=50, blank=True, help_text="Remarks can have max of 50 characters, blank=True")
    ref_credit_clearance = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"id : {self.id}"


register(CreditClearance, app="log_app", table_name="credit_management_creditclearance_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class CreditPaymentDetail(CreateInfoModel):
    credit_clearance = models.ForeignKey(CreditClearance, on_delete=models.PROTECT,
                                         related_name="credit_payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(decimal_places=2, max_digits=12, help_text="max_value upto 9999999999.99")
    payment_id = models.CharField(max_length=255, blank=True,help_text="Payment Mode ID, Esewa No/Khalti No/Cheque No")
    remarks = models.CharField(max_length=50, blank=True,
                               help_text="Remarks can have max of 50 characters, blank=True")

    def __str__(self):
        return f"{self.id}"


register(CreditPaymentDetail, app="log_app", table_name="credit_management_creditpaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
