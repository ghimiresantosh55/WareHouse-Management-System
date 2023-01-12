from django.db import models
from django.utils import timezone
# from src.core_app.models import CreateInfoModel
from ims import settings
from log_app.models import LogBase
# imports for log
from simple_history import register
from src.custom_lib.functions.date_converter import ad_to_bs_converter


class CustomGroup(models.Model):
    name = models.CharField(max_length=50, help_text="Name can have max of 50 characters")
    is_active = models.BooleanField(default=True, help_text="by default=True")
    permissions = models.ManyToManyField('CustomPermission', blank=True, help_text="blank=True")
    created_date_ad = models.DateTimeField(default=timezone.now)
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk} : {self.name}"

    def save(self, *args, **kwargs):
        # saving created_date_ad and bs, when it is a create operation
        if not self.id:
            self.created_date_ad = timezone.now()
            date_bs = ad_to_bs_converter(self.created_date_ad)
            self.created_date_bs = date_bs

        super().save(*args, **kwargs)


register(CustomGroup, app="log_app", table_name="user_group_customgroup_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PermissionCategory(models.Model):
    name = models.CharField(max_length=50, help_text="Name can have max of 50 characters")
    created_date_ad = models.DateTimeField(default=timezone.now)
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"ID-{self.id} : {self.name}"

    def save(self, *args, **kwargs):
        # saving created_date_ad and bs, when it is a create operation
        if not self.id:
            self.created_date_ad = timezone.now()
            date_bs = ad_to_bs_converter(self.created_date_ad)
            self.created_date_bs = date_bs

        super().save(*args, **kwargs)


register(PermissionCategory, app="log_app", table_name="user_group_permissioncategory_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class CustomPermission(models.Model):
    name = models.CharField(max_length=50, help_text="Name can have max of 50 characters")
    code_name = models.CharField(max_length=50, help_text="Code Name can have max of 50 characters")
    category = models.ForeignKey('PermissionCategory', on_delete=models.PROTECT, null=True, blank=True,
                                 help_text="null=Ture, blank=True")
    created_date_ad = models.DateTimeField(default=timezone.now)
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.category} : {self.code_name} "

    def save(self, *args, **kwargs):

        self.code_name = str(self.code_name).lower()
        # saving created_date_ad and bs, when it is a create operation
        if not self.id:
            self.created_date_ad = timezone.now()
            date_bs = ad_to_bs_converter(self.created_date_ad)
            self.created_date_bs = date_bs
        super().save(*args, **kwargs)


register(CustomPermission, app="log_app", table_name="user_group_custompermission_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])



