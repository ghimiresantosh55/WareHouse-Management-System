# third-party
from decimal import Decimal
from typing import Collection, Optional

import nepali_datetime
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
# Django
from django.db import models
from simple_history import register

# import for log
from log_app.models import LogBase
# User-defined models (import)
from src.core_app.models import (AdditionalChargeType, Country, CreateInfoModel, DiscountScheme,
                                 FiscalSessionAD, FiscalSessionBS, PaymentMode, validate_image, Currency)
from src.department.models import Department
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail
from src.supplier.models import Supplier


class PurchaseOrderMaster(CreateInfoModel):
    PURCHASE_ORDER_TYPE = (
        (1, "ORDER"),
        (2, "CANCELLED"),
        (3, "RECEIVED"),
        (4, "VERIFIED")
    )

    order_no = models.CharField(max_length=20, unique=True,
                                help_text="Order no. should be max. of 20 characters")
    order_type = models.PositiveIntegerField(choices=PURCHASE_ORDER_TYPE,
                                             help_text="Order type like Order, approved, cancelled")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name="department_purchase_orders")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Sub total can have max value upto=9999999999.99 and default=0.0")
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount can have max value upto=9999999999.99 and default=0.0")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if discountable, max_value=100.00 and default=0.0")
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can have max_value upto=9999999999.99 and min value=0.0")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount can have max value upto=9999999999.99 default=0.0")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount can have max value upto=9999999999.99 and default=0.0")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Total tax can have max value upto=9999999999.99 and default=0.0")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total can have max value upto=9999999999.99 and default=0.0")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT,
                                 help_text="Supplier")
    currency = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.PROTECT,
                                 help_text="Currency For Foreign exchange")
    currency_exchange_rate = models.DecimalField(
        max_digits=10, decimal_places=5, default=Decimal("0.00"),
        help_text="exchange rate max 10 digits with 5 decimal places"
    )
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters")
    terms_of_payment = models.TextField(blank=True)
    shipment_terms = models.TextField(blank=True)
    attendee = models.CharField(max_length=150, blank=True, help_text="Name of Attendee max = 150")
    end_user_name = models.CharField(max_length=100, blank=True)
    ref_purchase_order = models.ForeignKey('self', on_delete=models.PROTECT, related_name="self_purchase_order_master",
                                           blank=True, null=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.order_no)


register(PurchaseOrderMaster, app="log_app", table_name="purchase_purchaseordermaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseOrderDetail(CreateInfoModel):
    purchase_order = models.ForeignKey('PurchaseOrderMaster',
                                       related_name="purchase_order_details", on_delete=models.PROTECT)

    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    qty = models.DecimalField(max_digits=12, decimal_places=2, help_text="Order quantity")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    packing_type = models.ForeignKey(PackingType, on_delete=models.PROTECT)
    packing_type_detail = models.ForeignKey(PackingTypeDetail, on_delete=models.PROTECT)
    taxable = models.BooleanField(default=True, help_text="Check if item is taxable")
    tax_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                   help_text="Tax rate if item is taxable")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable")
    discount_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                        help_text="Discount rate if item is discountable")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    ref_purchase_order_detail = models.ForeignKey('self', on_delete=models.PROTECT, blank=True,
                                                  null=True, related_name='self_purchase_order_detail')
    cancelled = models.BooleanField(default=False)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.purchase_order)


register(PurchaseOrderDetail, app="log_app", table_name="purchase_purchaseorderdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseMaster(CreateInfoModel):
    PURCHASE_TYPE = (
        (1, "PURCHASE"),
        (2, "RETURN"),
        (3, "OPENING-STOCK"),
        (4, "STOCK-ADDITION"),
        (5, "STOCK-SUBTRACTION"),
        (6, "STOCK-DEPARTMENT"),
        (7, "STOCK-TASK"),
    )

    PAY_TYPE = (
        (1, "CASH"),
        (2, "CREDIT")
    )

    purchase_no = models.CharField(max_length=20, unique=True,
                                   help_text="Purchase no. should be max. of 10 characters")
    purchase_type = models.PositiveIntegerField(choices=PURCHASE_TYPE,
                                                help_text="Purchase type like 1= Purchase, 2 = Return, "
                                                          "3 = Opening stock, 4 = stock-addition, 5 = stock-subtraction")
    pay_type = models.PositiveIntegerField(choices=PAY_TYPE,
                                           help_text="Pay type like CASH, CREDIT")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name="department_stock")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2,
                                    help_text="Sub total can be max upto 9999999999.99")
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount can be max upto 9999999999.99")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if  discountable, default=0.0 and max_value=100.00")
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can be max upto 9999999999.99")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount can be max upto 9999999999.99")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount can be max upto 9999999999.99")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Total tax can be max upto 9999999999.99")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total can be max upto 9999999999.99")
    round_off_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                           help_text="Round off Amount can be max upto 9999999999.99")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, help_text="Supplier null=True")
    bill_no = models.CharField(max_length=20, help_text="Bill no.", blank=True)
    bill_date_ad = models.DateField(max_length=10, help_text="Bill Date AD", blank=True, null=True)
    bill_date_bs = models.CharField(max_length=10, help_text="Bill Date BS", blank=True)
    chalan_no = models.CharField(max_length=15, help_text="Chalan no.", blank=True)
    due_date_ad = models.DateField(max_length=10, help_text="Due Date AD", blank=True, null=True)
    due_date_bs = models.CharField(max_length=10, help_text="Due Date BS", blank=True)
    fiscal_session_ad = models.ForeignKey(FiscalSessionAD, on_delete=models.PROTECT)
    fiscal_session_bs = models.ForeignKey(FiscalSessionBS, on_delete=models.PROTECT)
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks can be max. of 100 characters")
    ref_purchase = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    ref_purchase_order = models.ForeignKey('PurchaseOrderMaster', on_delete=models.PROTECT,
                                           blank=True, null=True)
    ref_department_transfer_master = models.PositiveBigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.bill_date_ad is not None:
            date_bs_bill = nepali_datetime.date.from_datetime_date(self.bill_date_ad)
            self.bill_date_bs = date_bs_bill
        if self.due_date_ad is not None:
            date_bs_due = nepali_datetime.date.from_datetime_date(self.due_date_ad)
            self.due_date_bs = date_bs_due

        super().save(*args, **kwargs)

    def __str__(self):
        return "id {} : {}".format(self.id, self.purchase_no)


register(PurchaseMaster, app="log_app", table_name="purchase_purchasemaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseDetail(CreateInfoModel):
    purchase = models.ForeignKey(PurchaseMaster, related_name="purchase_details",
                                 on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                        help_text="purchase_cost can be max value upto 9999999999.99 and default=0.0")
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2,
                                    help_text="sale_cost can be max value upto 9999999999.99 and default=0.0")
    qty = models.DecimalField(max_digits=12, decimal_places=2,
                              help_text="Purchase quantity can be max value upto 9999999999.99 and default=0.0")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    free_purchase = models.BooleanField(default=False, help_text="default = false")
    packing_type = models.ForeignKey(PackingType, on_delete=models.PROTECT)
    packing_type_detail = models.ForeignKey(PackingTypeDetail, on_delete=models.PROTECT)
    taxable = models.BooleanField(default=True, help_text="Check if item is taxable")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                   help_text="Tax rate if item is taxable, max value=100.00 and default=0.0")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                     help_text="Tax amount can be max value upto 9999999999.99 and default=0.0")
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable")
    expirable = models.BooleanField(default=False, help_text="Check if item is Expirable, default=False")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if item is discountable, default=0.0 and max_value=100.00")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                          help_text="Discount_amount can be max upto 9999999999.99 and default=0.0")
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                       help_text="Gross amount can be max upto 9999999999.99 and default=0.0")
    net_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                     help_text="Net amount can be max upto 9999999999.99 and default=0.0")
    expiry_date_ad = models.DateField(max_length=10, help_text="Expiry Date AD", null=True, blank=True)
    expiry_date_bs = models.CharField(max_length=10, help_text="Expiry Date BS", blank=True)
    batch_no = models.CharField(max_length=20, help_text="Batch no. max length 20")
    ref_purchase_order_detail = models.ForeignKey('PurchaseOrderDetail', on_delete=models.PROTECT,
                                                  blank=True, null=True)
    ref_transfer_detail = models.PositiveBigIntegerField(default=0)
    ref_department_transfer_detail = models.PositiveBigIntegerField(default=0)
    ref_purchase_detail = models.ForeignKey('self', related_name='self_ref_purchase_detail', on_delete=models.PROTECT,
                                            blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.expiry_date_ad is not None:
            date_bs = nepali_datetime.date.from_datetime_date(self.expiry_date_ad)
            self.expiry_date_bs = date_bs
        super().save(*args, **kwargs)

    def __str__(self):
        return "id {}: {}".format(self.id, self.purchase.purchase_no)


register(PurchaseDetail, app="log_app", table_name="purchase_purchasedetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchasePaymentDetail(CreateInfoModel):
    purchase_master = models.ForeignKey(PurchaseMaster, on_delete=models.PROTECT, related_name="payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 help_text="Amount can have max value upto 9999999999.99 and min=0.0")
    payment_id = models.CharField(max_length=255, blank=True, help_text="Payment Mode ID, Esewa No/Khalti No/Cheque No")
    remarks = models.CharField(max_length=50, blank=True,
                               help_text="Remarks can have max upto 50 characters")

    def __str__(self):
        return f"{self.id}"


register(PurchasePaymentDetail, app="log_app", table_name="purchase_purchasepaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseAdditionalCharge(CreateInfoModel):
    charge_type = models.ForeignKey(AdditionalChargeType, on_delete=models.PROTECT)
    purchase_master = models.ForeignKey(PurchaseMaster, on_delete=models.PROTECT, related_name="additional_charges")
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 help_text="Amount can have max value upto 9999999999.99 and min=0.0")
    remarks = models.CharField(max_length=50, blank=True,
                               help_text="Remarks can have max upto 50 characters")

    def __str__(self):
        return "id {} purchase {} charge {}".format(self.id, self.purchase_master.purchase_no, self.charge_type.name)


register(PurchaseAdditionalCharge, app="log_app", table_name="purchase_purchaseadditionalcharge_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseDocumentType(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def validate_unique(self, exclude: Optional[Collection[str]] = ...) -> None:
        # Custom unique validation check for case insensitive
        if self.id:
            if PurchaseDocumentType.objects.exclude(id=self.id).filter(name__iexact=self.name).exists():
                raise ValidationError("this ItemUnit name already exists")
        else:
            if PurchaseDocumentType.objects.filter(name__iexact=self.name).exists():
                raise ValidationError("this item unit name already exists")
        return super().validate_unique(exclude)

    def __str__(self):
        return f"{self.id} : {self.name}"


register(PurchaseDocumentType, app="log_app", table_name="purchase_purchasedocumenttype_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseDocument(CreateInfoModel):
    title = models.CharField(max_length=50, blank=True)
    purchase_document_type = models.ForeignKey(PurchaseDocumentType, on_delete=models.PROTECT, related_name="documents")
    purchase_main = models.ForeignKey(PurchaseMaster, on_delete=models.PROTECT, related_name="purchase_documents")
    document_url = models.FileField(upload_to='purchase-documents/', validators=[validate_image])
    remarks = models.CharField(max_length=100, help_text="maxlength = 100", blank=True)


register(PurchaseDocument, app="log_app", table_name="purchase_purchasedocument_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseOrderDocument(CreateInfoModel):
    title = models.CharField(max_length=50, blank=True)
    document_type = models.ForeignKey(PurchaseDocumentType, on_delete=models.PROTECT, related_name="purchase_order")
    purchase_order = models.ForeignKey(PurchaseOrderMaster, on_delete=models.PROTECT,
                                       related_name="purchase_order_documents")
    document_url = models.FileField(upload_to='purchase-order-documents/', validators=[validate_image])
    remarks = models.CharField(max_length=100, help_text="maxlength = 100", blank=True)


register(PurchaseOrderDocument, app="log_app", table_name="purchase_purchaseorderdocument_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
