from django.contrib import admin

# Register your models here.
from .models import Audit, AuditDetail

admin.site.register(Audit)
admin.site.register(AuditDetail)
