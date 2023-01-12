from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from django.db import models
from simple_history import register

from log_app.models import LogBase
from src.custom_lib.functions.date_converter import ad_to_bs_converter

User = get_user_model()


def upload_path_organization(instance, filename):
    return '/'.join(['organization', filename])


def upload_path_flag_image(instance, filename):
    return '/'.join(['country_flag', filename])


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)


def validate_organization_setup_images(image):
    file_size = image.size
    limit_byte_size = 20480
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        raise ValidationError("Max size of file is %s KB" % f)


class CreateInfoModel(models.Model):
    """
    Parent model for created date ad, created date bs and created by and device type, app type
    """
    DEVICE_TYPE = [
        (1, "Mobile"),
        (2, "PC"),
        (3, "Tablet"),
        (4, "Other"),
        (5, "NA")
    ]
    APP_TYPE = [
        (1, 'Web-App'),
        (2, 'IOS-App'),
        (3, 'Android-App'),
        (4, "NA")

    ]

    created_date_ad = models.DateTimeField()
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    device_type = models.PositiveBigIntegerField(choices=DEVICE_TYPE, default=5,
                                                 help_text="where 1=Mobile, 2=PC, 3=Tablet and 4=Other")
    app_type = models.PositiveBigIntegerField(choices=APP_TYPE, default=4,
                                              help_text="where 1=Web-App, 2=IOS-APP, 3=Android-APP")

    def save(self, *args, **kwargs):
        '''
        This method will convert ad date to bs date
        '''
        self.created_date_bs = ad_to_bs_converter(self.created_date_ad)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Country(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="Name of the country can have max upto 50 characters, unique=True")
    country_code = models.CharField(max_length=5, blank=True, null=True,
                                    help_text="country_code can be have max upto 5 characters and null=True, blank=True")
    phone_code = models.CharField(max_length=5, blank=True, null=True,
                                  help_text="phone_code can be have max upto 5 characters and null=True, blank=True")
    flag_image = models.ImageField(upload_to="flag_image", validators=[validate_image], blank=True,
                                   help_text="Image can be max of 2 MB size, blank=True")
    active = models.BooleanField(default=True, help_text="By default=true")

    def __str__(self):
        return f"{self.name}"


register(Country, app="log_app", table_name="core_app_country_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Currency(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="currency_name can be have max upto 50 characters and null=True, "
                                      "blank=True")
    symbol = models.CharField(max_length=3, blank=True, null=True,
                              help_text="currency_symbol can be have max upto 3 characters and null=True, "
                                        "blank=True")
    code = models.CharField(max_length=3, blank=True, null=True,
                            help_text="currency_name can be have max upto 3 characters and null=True, "
                                      "blank=True")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id}: {self.name}'


register(Currency, app="log_app", table_name="core_app_currency_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Province(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="Province name can be max. of 50 characters and unique=True")
    active = models.BooleanField(default=True, help_text="by default=True")

    def __str__(self):
        return f"{self.name}"


register(Province, app="log_app", table_name="core_app_province_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class District(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="District name can be max. of 50 characters and unique=True")
    province = models.ForeignKey(Province, on_delete=models.PROTECT, help_text="Fk Province")
    active = models.BooleanField(default=True, help_text="by default=True")

    def __str__(self):
        return f"{self.name}"


register(District, app="log_app", table_name="core_app_district_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class OrganizationSetup(CreateInfoModel):
    name = models.CharField(max_length=100, unique=True,
                            help_text="Organization name should be maximum of 100 characters")
    address = models.CharField(max_length=100, unique=True, blank=True,
                               help_text="Organization name should be maximum of 100 characters")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True,
                                help_text="blank= True and null= True")
    phone_no_1 = models.CharField(max_length=15, unique=True, blank=True,
                                  help_text="Phone no should be maximum of 15 characters")
    phone_no_2 = models.CharField(max_length=15, blank=True, help_text="Phone no should be maximum of 15 characters")
    mobile_no = models.CharField(max_length=15, unique=True, blank=True,
                                 help_text="Mobile no should be maximum of 15 characters")
    pan_no = models.CharField(max_length=15, unique=True, blank=True,
                              help_text="PAN no. should be maximum of 15 characters")
    owner_name = models.CharField(max_length=50, unique=True, blank=True,
                                  help_text="Owner name should be maximum of 50 characters")
    email = models.CharField(max_length=70, unique=True, blank=True,
                             help_text="Email Id. should be maximum of 70 characters")
    website_url = models.CharField(max_length=50, unique=True, blank=True,
                                   help_text="Website address should be maximum of 50 characters")
    logo = models.ImageField(upload_to="organization_setup/logo",
                             validators=[validate_organization_setup_images,
                                         FileExtensionValidator(allowed_extensions=['png'])],
                             blank=True, help_text="",
                             default='default_images/soori.png')
    favicon = models.ImageField(upload_to="organization_setup/favicon", validators=[validate_organization_setup_images],
                                blank=True,
                                null=True, help_text="",
                                default='default_images/favicon.ico')
    stamp = models.ImageField(upload_to="organization_setup/stamp", validators=[validate_organization_setup_images],
                              blank=True, help_text="stamp image of organization",
                              default='default_images/stamp.png')
    signature = models.ImageField(upload_to="organization_setup/signature", blank=True,
                                  validators=[validate_organization_setup_images],
                                  null=True, help_text="signature image of organization owner",
                                  default='default_images/signature.png')

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)

    def save(self, *args, **kwargs):
        if self.logo:
            super().save(*args, **kwargs)
            img = Image.open(self.logo.path)  # Open image using self
            width, height = img.size
            new_width = 0.5 * width
            new_size = (int(new_width), 36)
            img.resize(new_size, Image.ANTIALIAS)
            img.save(self.logo.path)


register(OrganizationSetup, app="log_app", table_name="core_app_organizationsetup_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class OrganizationRule(CreateInfoModel):
    CUSTOMER_SEQUENCE_TYPE = [
        (1, "AD"),
        (2, "BS"),
        (3, "SEQUENTIAL")
    ]

    CALENDAR_SYSTEM = [
        (1, "AD"),
        (2, "BS")
    ]

    DAYS_OF_WEEK = [
        (1, "SUNDAY"),
        (2, "MONDAY"),
        (3, "TUESDAY"),
        (4, "WEDNESDAY"),
        (5, "THURSDAY"),
        (6, "FRIDAY"),
        (7, "SATURDAY"),
    ]

    TAX_SYSTEM = [
        (1, "VAT"),
        (2, "PAN")
    ]
    customer_seq_type = models.PositiveIntegerField(choices=CUSTOMER_SEQUENCE_TYPE, default=2,
                                                    help_text="where 1=AD,2=BS,3=SEQUENTIAL  and default=2")
    fiscal_session_type = models.PositiveIntegerField(choices=CALENDAR_SYSTEM, default=2,
                                                      help_text="Where 1 = AD , 2 = BS and default=2")
    calendar_system = models.PositiveIntegerField(choices=CALENDAR_SYSTEM, default=2,
                                                  help_text="Where 1 = AD , 2 = BS and default=2")
    enable_print = models.BooleanField(default=True)
    print_preview = models.BooleanField(default=True)
    billing_time_restriction = models.BooleanField(default=False)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    first_day_of_week = models.PositiveIntegerField(choices=DAYS_OF_WEEK, default=1,
                                                    help_text="where 1 = Sunday ---- 7 =Saturday")
    tax_system = models.PositiveIntegerField(choices=TAX_SYSTEM, default=1, help_text="where 1=VAT, 2=PAN")
    round_off_limit = models.PositiveIntegerField(default=2)
    round_off_purchase = models.BooleanField(default=True)
    round_off_sale = models.BooleanField(default=True)
    item_expiry_date_sale_threshold = models.PositiveIntegerField(default=30)
    tax_applicable = models.BooleanField(default=True)
    tax_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                 help_text="Tax rate")

    def __str__(self):
        return "id {} : {}".format(self.id, self.get_calendar_system_display())


register(OrganizationRule, app="log_app", table_name="core_app_organizationrule_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Bank(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)


register(Bank, app="log_app", table_name="core_app_bank_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class BankDeposit(CreateInfoModel):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    deposit_date_ad = models.DateTimeField()
    deposit_date_bs = models.CharField(max_length=10, blank=True)
    deposit_by = models.CharField(max_length=50, help_text="max length can be 50 characters")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="User can input value upto 99999999.99")
    remarks = models.CharField(max_length=50, blank=True, help_text="max length can be 50 characters and blank=True")

    def save(self, *args, **kwargs):
        self.deposit_date_bs = ad_to_bs_converter(self.deposit_date_ad)
        super().save(*args, **kwargs)

    def __str__(self):
        return "id {} : deposited by {} to {} bank".format(self.id, self.deposit_by, self.bank.name)


register(BankDeposit, app="log_app", table_name="core_app_bankdeposit_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PaymentMode(CreateInfoModel):
    payment_types = [
        (1, "CASH"),
        (2, "BANK"),
        (3, "WALLET"),

    ]
    type = models.PositiveIntegerField(choices=payment_types, default=1)
    name = models.CharField(max_length=15, unique=True, help_text="Name can have max upto 15 character, unique=True")
    active = models.BooleanField(default=0, help_text="by default=0")
    remarks = models.CharField(max_length=50, blank=True,
                               help_text="remarks can have max upto 50 character, blank=True")

    def __str__(self):
        return f"{self.name}"


register(PaymentMode, app="log_app", table_name="core_app_paymentmode_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class DiscountScheme(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="Discount scheme name must be max 50 characters, uqique=True")
    editable = models.BooleanField(default=False, help_text="default=False")
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                               help_text="Discount Rate default=0.00 max upto 100.00")
    active = models.BooleanField(default=True, help_text="by default=True")

    def __str__(self):
        return f"{self.name}"


register(DiscountScheme, app="log_app", table_name="core_app_discountscheme_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AdditionalChargeType(CreateInfoModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="Additional Charge type name must be max 50 characters, unique=True")
    active = models.BooleanField(default=True, help_text="default=True")

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)


register(AdditionalChargeType, app="log_app", table_name="core_app_additionalchargetype_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class TaxGroup(CreateInfoModel):
    name = models.CharField(max_length=20, unique=True,
                            help_text="Name can have max of 20 characaters and must be unique")
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                               help_text="Default=0.0")
    display_order = models.IntegerField(default=0, help_text="Display order for ordering, default=0")
    active = models.BooleanField(default=True, help_text="By default active=True")


register(TaxGroup, app="log_app", table_name="core_app_taxgroup_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AppAccessLog(CreateInfoModel):
    DEVICE_TYPE = [
        (1, "Mobile"),
        (2, "PC"),
        (3, "Tablet"),
        (4, "Other")
    ]
    APP_TYPE = [
        (1, 'Web-App'),
        (2, 'IOS-App'),
        (3, 'Android-App')
    ]
    device_type = models.PositiveBigIntegerField(choices=DEVICE_TYPE, default="NA",
                                                 help_text="where 1=Mobile, 2=PC, 3=Tablet and 4=Other")
    app_type = models.PositiveBigIntegerField(choices=APP_TYPE, default="NA",
                                              help_text="where 1=Web-App, 2=IOS-APP, 3=Android-APP")

    def __str__(self):
        return f'{self.id}'


register(AppAccessLog, app="log_app", table_name="core_app_appaccesslog_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Store(CreateInfoModel):
    name = models.CharField(max_length=30, unique=True,
                            help_text="Name can have max of 30 characaters and must be Unique")
    code = models.CharField(max_length=7, unique=True, blank=True,
                            help_text="Item code should be max. of 10 characters")
    active = models.BooleanField(default=True, help_text="By default active=True")


register(Store, app="log_app", table_name="core_app_store_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class FiscalSessionAD(CreateInfoModel):
    session_full = models.CharField(max_length=9, unique=True, blank=True,
                                    help_text="Should be unique and must contain 9 characters")
    session_short = models.CharField(max_length=5, unique=True, blank=True,
                                     help_text="Should be unique and must contain 5 characters")


register(FiscalSessionAD, app="log_app", table_name="core_app_fiscal_session_ad_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class FiscalSessionBS(CreateInfoModel):
    session_full = models.CharField(max_length=9, unique=True, blank=True,
                                    help_text="Should be unique and must contain 9 characters")
    session_short = models.CharField(max_length=5, unique=True, blank=True,
                                     help_text="Should be unique and must contain 5 characters")


register(FiscalSessionBS, app="log_app", table_name="core_app_fiscal_session_bs_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
