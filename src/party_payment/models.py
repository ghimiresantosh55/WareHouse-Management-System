# third-party
import nepali_datetime
from django.db import models
from simple_history import register

# log import
from log_app.models import LogBase
from src.core_app.models import CreateInfoModel, PaymentMode, FiscalSessionAD, FiscalSessionBS
from src.purchase.models import PurchaseMaster
from src.supplier.models import Supplier


class PartyPayment(CreateInfoModel):
    PAYMENT_TYPE = (
        (1, "PAYMENT"),
        (2, "REFUND"),
    )

    purchase_master = models.ForeignKey(PurchaseMaster, on_delete=models.PROTECT, related_name='party_payments')
    payment_type = models.PositiveIntegerField(choices=PAYMENT_TYPE, default=0,
                                               help_text="Where 1 = PAYMENT, 2 = REFUND")
    receipt_no = models.CharField(max_length=20, help_text="Receipt no can have max of 20 characters")

    total_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                       help_text="max_value upto 9999999999.99 and min_vale=0.0")
    remarks = models.CharField(max_length=50, blank=True, help_text="Remarks can be max upto 50 characters, blank=True")
    ref_party_clearance = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"id : {self.id}"


register(PartyPayment, app="log_app", table_name="party_payment_partypayment_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PartyPaymentDetail(CreateInfoModel):
    party_payment = models.ForeignKey(PartyPayment, on_delete=models.PROTECT,
                                      related_name="party_payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 help_text="Maximum value 9999999999.99, min_value=0.0")
    payment_id = models.CharField(max_length=255, blank=True, help_text="Payment Mode ID, Esewa No/Khalti No/Cheque No")
    remarks = models.CharField(max_length=50, blank=True, help_text="Max upto 50 characters, blank=True")

    def __str__(self):
        return f"{self.id}"


register(PartyPaymentDetail, app="log_app", table_name="party_payment_partypaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class BasicPartyPayment(CreateInfoModel):
    PAYMENT_TYPE = (
        (1, "PAYMENT"),
        (2, "RETURN"),
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    payment_type = models.PositiveIntegerField(choices=PAYMENT_TYPE,
                                               help_text="Payment type like 1=PAYMENT, 2=RETURN")
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 help_text="Maximum value 9999999999.99, min_value=0.0")
    receipt_no = models.CharField(max_length=20, blank=True, null=True,
                                  help_text="Receipt no can have max of 20 characters and blank = true")
    payment_date_ad = models.DateField(max_length=10, help_text="Payment Date AD")
    payment_date_bs = models.CharField(max_length=10, help_text="Payment Date BS")
    fiscal_session_ad = models.ForeignKey(FiscalSessionAD, on_delete=models.PROTECT)
    fiscal_session_bs = models.ForeignKey(FiscalSessionBS, on_delete=models.PROTECT)
    remarks = models.CharField(max_length=100, blank=True, help_text="Max upto 100 characters, blank=True")

    def save(self, *args, **kwargs):
        if self.payment_date_ad is not None:
            bs_payment_date = nepali_datetime.date.from_datetime_date(self.payment_date_ad)
            self.payment_date_bs = bs_payment_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}"


register(BasicPartyPayment, app="log_app", table_name="basic_party_payment_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class BasicPartyPaymentDetail(CreateInfoModel):
    basic_party_payment = models.ForeignKey(BasicPartyPayment, on_delete=models.PROTECT,
                                            related_name="basic_party_payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 help_text="Maximum value 9999999999.99, min_value=0.0")
    remarks = models.CharField(max_length=100, blank=True, help_text="Max upto 100 characters, blank=True")

    def __str__(self):
        return f"{self.id}"


register(BasicPartyPaymentDetail, app="log_app", table_name="basic_party_payment_detail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
