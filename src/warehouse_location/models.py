from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.
from simple_history import register

from log_app.models import LogBase
from src.core_app.models import CreateInfoModel
from src.department.models import Department


class Location(MPTTModel, CreateInfoModel):
    name = models.CharField(max_length=50)
    prefix = models.CharField(max_length=3)
    code = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    remarks = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.id} : {self.name} : {self.code}"


register(Location, app="log_app", table_name="warehouse_location_location_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
