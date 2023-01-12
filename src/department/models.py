from simple_history import register

from log_app.models import LogBase


from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=20)
    allow_sales = models.BooleanField(default=False)
    created_date_ad = models.DateTimeField()
    created_date_bs = models.CharField(max_length=10)


register(Department, app="log_app",
         table_name="department_department_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs'],
         bases=[LogBase])
