from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Account, AccountGroup, VoucherDetail, VoucherMaster


# Register your models here.
class VoucherDetailInline(admin.StackedInline):
    model = VoucherDetail


class VoucherMasterAdmin(admin.ModelAdmin):
    inlines = [VoucherDetailInline, ]


admin.site.register(Account)
admin.site.register(AccountGroup, MPTTModelAdmin)
admin.site.register(VoucherMaster, VoucherMasterAdmin)
