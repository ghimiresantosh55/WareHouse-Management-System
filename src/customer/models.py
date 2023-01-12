# User-defined models (import)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from simple_history import register

from ims import settings
# log import
from log_app.models import LogBase
from src.core_app.models import Country, CreateInfoModel
from src.custom_lib.functions.field_value_validation import gt_zero_validator

User = get_user_model()


def upload_path_customer(instance, filename):
    return '/'.join(['customer_image', filename])


from src.supplier.models import Supplier


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)


class Customer(CreateInfoModel):
    TAX_REG_SYSTEM_TYPES = (
        (1, "VAT"),
        (2, "PAN")
    )
    user = models.OneToOneField(User, verbose_name=_("user"), blank=True, null=True, on_delete=models.PROTECT,
                                related_name="customer_info")
    first_name = models.CharField(max_length=40, help_text="First name should be max. of 40 characters")
    middle_name = models.CharField(max_length=40, blank=True, help_text="Middle name should be max. of 40 characters")
    last_name = models.CharField(max_length=40, blank=True, help_text="Last name should be max. of 40 characters")
    address = models.CharField(max_length=50, help_text="Address should be max. of 50 characters")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True,
                                help_text="blank= True and null= True")
    phone_no = models.CharField(max_length=15, blank=True, help_text="Phone no. should be max. of 15 characters")
    mobile_no = models.CharField(max_length=15, blank=True, help_text="mobile no. should be max. of 15 characters")
    email_id = models.CharField(max_length=50, blank=True, help_text="Email Id should be max. of 50 characters")
    pan_vat_no = models.CharField(max_length=9, blank=True, help_text="PAN/VAT should be max. of 15 characters")
    tax_reg_system = models.PositiveIntegerField(choices=TAX_REG_SYSTEM_TYPES, default=1,
                                                 help_text="default value is 1")
    image = models.ImageField(upload_to="customer", validators=[validate_image], blank=True,
                              help_text="max image size should be 2 MB")
    active = models.BooleanField(default=True)
    credit_limit = models.DecimalField(decimal_places=2, default=100000.00, max_digits=12,
                                       validators=[gt_zero_validator])

    def __str__(self):
        return self.first_name


register(Customer, app="log_app", table_name="customer_customer_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class CustomerIsSupplier(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_is_customer")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_is_supplier")

    class Meta:
        unique_together = ['supplier', 'customer']
