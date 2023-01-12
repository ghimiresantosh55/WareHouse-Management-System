from django.contrib import admin

# Register your models here.
from .models import Supplier


class SupplierAdminModel(admin.ModelAdmin):
    model = Supplier
    search_fields = ['name', ]
    ordering = ['id', 'name']
    list_display = ['id', 'name',  'pan_vat_no',
                    'phone_no', 'email_id']


admin.site.register(Supplier, SupplierAdminModel)