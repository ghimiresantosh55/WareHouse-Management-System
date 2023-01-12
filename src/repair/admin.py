from django.contrib import admin
from.models import Repair, RepairDetail,RepairUser

# Register your models here.
admin.site.register(RepairUser)
admin.site.register(Repair)
admin.site.register(RepairDetail)