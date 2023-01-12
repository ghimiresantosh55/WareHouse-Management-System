from datetime import date, timedelta
from decimal import Decimal

import nepali_datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError
from simple_history import register

from log_app.models import LogBase
from src.core_app.models import CreateInfoModel
from src.item.models import Item
from src.item_serialization.models import PackingTypeDetailCode
from src.warehouse_location.models import Location

User = get_user_model()


class AssetCategory(CreateInfoModel):
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True, help_text="By default=true")


register(AssetCategory, app="log_app", table_name="asset_category_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetSubCategory(CreateInfoModel):
    asset_category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True, help_text="By default=true")


register(AssetSubCategory, app="log_app", table_name="asset_sub_category_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Asset(CreateInfoModel):
    DEPRECIATION_METHODS = (
        (1, "STRAIGHT-LINE"),
        (2, "DECLINING-BALANCE"),
    )

    registration_no = models.CharField(max_length=20, unique=True, blank=True,
                                       help_text="registration no. should be max. of 10 characters")
    scrapped = models.BooleanField(default=False, help_text="default = False")
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, null=True, blank=True)
    sub_category = models.ForeignKey(AssetSubCategory, on_delete=models.PROTECT, null=True, blank=True)
    available = models.BooleanField(default=True, help_text="default = True")
    qty = models.PositiveIntegerField(help_text="no of assets")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    adjusted_book_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    net_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters")

    salvage_value = models.DecimalField(max_digits=7, default=Decimal("0.00"), decimal_places=2,
                                        help_text="value of asset after its full use")
    depreciation_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"),
                                            help_text="Rate of Depreciation")
    amc_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"),
                                   help_text="Annual Maintenance Charge Rate")
    depreciation_method = models.IntegerField(
        choices=DEPRECIATION_METHODS, default=1,
        help_text="deprecation method : 1 = STRAIGHT-LINE, 2 = DECLINING-BALANCE, default value is = 1"
    )
    end_of_life_in_years = models.PositiveIntegerField(default=1)
    warranty_duration = models.DurationField(default=timedelta())
    maintenance_duration = models.DurationField(default=timedelta())
    bulk_update = models.BooleanField(default=False, help_text="By default=false")

    def __str__(self):
        return "id {}".format(self.id)

    @property
    def deprecated_value(self):
        purchase_cost = self.item.purchase_cost
        print(purchase_cost, "this is purchase cost")
        time_duration = relativedelta(date.today(), self.created_date_ad.date()).years
        if self.depreciation_method == 1:
            if time_duration > self.end_of_life_in_years:
                return self.salvage_value

            deprecated_amount = purchase_cost - self.salvage_value / self.end_of_life_in_years
            print(deprecated_amount, "this is deprecated value")
            return purchase_cost - (deprecated_amount * time_duration)
        else:
            return self.salvage_value

    @property
    def near_end_life_days(self):
        end_of_life_date = self.created_date_ad.date() + relativedelta(years=self.end_of_life_in_years)
        near_end = end_of_life_date - date.today()
        return near_end.days

    @property
    def rem_maintenance_days(self):
        maintenance_days = self.maintenance_duration.days
        asset_service = AssetService.objects.filter(asset=self.id).order_by("id").last()
        if asset_service:
            if asset_service.service_status == 1:
                return 0
            else:
                remaining_days = asset_service.receive_date_ad.date() + \
                                 relativedelta(days=maintenance_days) - date.today()
                return remaining_days.days
        remaining_days = (self.created_date_ad.date() + relativedelta(days=maintenance_days)) - date.today()
        return remaining_days.days

    @property
    def rem_warranty_days(self):
        rem_warranty_days = (self.created_date_ad.date() + relativedelta(
            days=self.warranty_duration.days)) - date.today()
        return rem_warranty_days


register(Asset, app="log_app", table_name="asset_asset_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetList(CreateInfoModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="asset_details")
    packing_type_detail_code = models.OneToOneField(PackingTypeDetailCode, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="asset_location", null=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.packing_type_detail_code)


register(AssetList, app="log_app", table_name="asset_assetlist_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetIssue(CreateInfoModel):
    ISSUE_TYPE = (
        (1, "ISSUED"),
        (2, "RETURNED")
    )
    issue_type = models.PositiveIntegerField(choices=ISSUE_TYPE,
                                             help_text="Order type like Issued, Returned")
    asset = models.ForeignKey(AssetList, on_delete=models.PROTECT)
    issued_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name="asset_issued_by")
    due_date_ad = models.DateField(help_text="Due Date AD")
    due_date_bs = models.CharField(max_length=10, help_text="Due Date BS")
    return_date_ad = models.DateField(null=True, blank=True, help_text="Due Date AD")
    return_date_bs = models.CharField(max_length=10, blank=True, help_text="Due Date BS")
    return_received_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True,
                                           related_name="asset_return_received_by")
    remarks = models.CharField(max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")

    def save(self, *args, **kwargs):
        if not self.id:
            self.due_date_bs = nepali_datetime.date.from_datetime_date(self.due_date_ad)
        if self.return_date_ad:
            self.return_date_bs = nepali_datetime.date.from_datetime_date(self.return_date_ad)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.id}"


register(AssetIssue, app="log_app", table_name="asset_assetissue_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetService(CreateInfoModel):
    SERVICE_STATUS = (
        (1, "PENDING"),
        (2, "REPAIRED")
    )
    service_status = models.PositiveIntegerField(choices=SERVICE_STATUS,
                                                 help_text="Status like PENDING, REPAIRED")
    asset = models.ForeignKey(AssetList, on_delete=models.PROTECT)
    receive_date_ad = models.DateField(help_text="Due Date AD", null=True, blank=True)
    receive_date_bs = models.CharField(max_length=10, help_text="Due Date BS", null=True, blank=True)
    solution = models.CharField(max_length=100, blank=True, help_text="Solution should be max. of 100 characters")
    taken_by = models.CharField(max_length=50, blank=True, help_text="Taken by should be max. of 50 characters")
    problem = models.CharField(max_length=100, blank=True, help_text="Problem should be max. of 100 characters")
    remarks = models.CharField(max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")

    def save(self, *args, **kwargs):
        if self.id:
            self.receive_date_bs = nepali_datetime.date.from_datetime_date(self.receive_date_ad)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.id}"


#
register(AssetService, app="log_app", table_name="asset_assetservice_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetDispatch(CreateInfoModel):
    DISPATCH_INFO = (
        (1, "DISPATCH"),
        (2, "RETURN")
    )
    DISPATCH_TYPE = (
        (1, "INTERNAL"),
        (2, "EXTERNAL"),
    )
    DISPATCH_SUB_TYPE = (
        (1, "MAINTENANCE"),
        (2, "TRANSFER")
    )
    receiver_name = models.CharField(max_length=200, help_text="Name of the receiver, can be of max 200 characters")
    receiver_id_no = models.CharField(max_length=50, blank=True, help_text="Receiver Id No of the user")
    dispatch_no = models.CharField(max_length=20, unique=True, help_text="Dispatch No, can be of max. 20 characters")
    dispatch_type = models.CharField(choices=DISPATCH_TYPE, max_length=10,
                                     help_text="Dispatch type choices max of 10 characters, where 1=INTERNAL and"
                                               "2=EXTERNAL")
    dispatch_info = models.CharField(choices=DISPATCH_INFO, max_length=10,
                                     help_text="Dispatch info choices max of 10 characters, where 1=DISPATCH, 2=RETURN")
    dispatch_sub_type = models.CharField(choices=DISPATCH_SUB_TYPE, null=True, max_length=15,
                                         help_text="Dispatch Sub Type choices, max of 15 characters,"
                                                   " where 1=MAINTENANCE and"
                                                   "2=TRANSFER")
    dispatch_by = models.ForeignKey(User, on_delete=models.PROTECT,
                                    help_text="dispatch by user", related_name="asset_dispatch_by")
    returned_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT,
                                    help_text="Returned by user", related_name="asset_dispatch_return_by")
    dispatch_to = models.ForeignKey(User, on_delete=models.PROTECT,
                                    help_text="dispatch to user", related_name="asset_dispatch_to")
    ref_dispatch = models.ForeignKey('self', on_delete=models.PROTECT, related_name="ref_asset_dispatch")
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters and blank=True")

    def __str__(self):
        return f"{self.id} : {self.dispatch_no}"

    def save(self, *args, **kwargs):
        if self.dispatch_type == 2:
            if self.dispatch_sub_type is None:
                raise ValidationError("You must provide dispatch sub type if dispatch type is set to external")
        super(AssetDispatch, self).save(*args, **kwargs)


register(AssetDispatch, app="log_app", table_name="asset_assetdispatch_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetDispatchDetail(CreateInfoModel):
    asset_dispatch = models.ForeignKey(AssetDispatch, on_delete=models.PROTECT, related_name="asset_dispatches")
    asset_detail = models.ForeignKey(AssetList, on_delete=models.PROTECT, related_name="asset_dispatch_asset")
    picked = models.BooleanField(default=False, help_text="Asset Picked boolean, is default to False")
    picked_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True,
                                  related_name="dispatch_details_picked")
    ref_dispatch_detail = models.ForeignKey('self', on_delete=models.PROTECT, related_name="ref_asset_dispatch_detail")

    def __str__(self):
        return self.id


register(AssetDispatchDetail, app="log_app", table_name="asset_assetdispatch_detail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetMaintenance(CreateInfoModel):
    maintenance_no = models.CharField(max_length=20, unique=True,
                                      help_text="Asset Repair no, can have max of 20 characters")
    next_maintenance_date = models.DateField()
    issued_to = models.ForeignKey(User, null=True, on_delete=models.PROTECT, related_name="asset_maintenance_issued")
    issue_reasons = models.TextField(blank=True)
    expected_return_date = models.DateField()
    asset_dispatch = models.ForeignKey(AssetDispatch, on_delete=models.PROTECT,
                                       related_name="asset_maintenance")

    def __str__(self):
        return f"{self.id} : {self.maintenance_no}"


register(AssetMaintenance, app="log_app", table_name="asset_asset_maintenance_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AssetTransfer(CreateInfoModel):
    transfer_no = models.CharField(max_length=20, unique=True,
                                   help_text="Asset Transfer no, can have max of 20 characters")
    asset_dispatch = models.ForeignKey(AssetDispatch, on_delete=models.PROTECT,
                                       related_name="asset_transfer")
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters and blank=True")

    def __str__(self):
        return f"{self.id} : {self.transfer_no}"


register(AssetTransfer, app="log_app", table_name="asset_assettranfer_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
