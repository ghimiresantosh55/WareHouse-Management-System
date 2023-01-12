from django.contrib import admin
from .models import DepartmentTransferMaster, DepartmentTransferDetail
# Register your models here.


admin.site.register(DepartmentTransferDetail)
admin.site.register(DepartmentTransferMaster)