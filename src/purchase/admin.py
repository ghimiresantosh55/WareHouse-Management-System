from django.contrib import admin

from .models import PurchaseOrderMaster, PurchaseOrderDetail, PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, \
    PurchaseAdditionalCharge


class PurchaseOrderDetailInline(admin.StackedInline):
    model = PurchaseOrderDetail


class PurchaseOrderMasterAdmin(admin.ModelAdmin):
    inlines = [PurchaseOrderDetailInline, ]


class PurchaseDetailInline(admin.StackedInline):
    model = PurchaseDetail


class PurchaseMasterAdmin(admin.ModelAdmin):
    inlines = [PurchaseDetailInline, ]


admin.site.register(PurchaseOrderDetail)
admin.site.register(PurchaseOrderMaster, PurchaseOrderMasterAdmin)
admin.site.register(PurchaseMaster, PurchaseMasterAdmin)
admin.site.register(PurchaseDetail)
admin.site.register(PurchasePaymentDetail)
admin.site.register(PurchaseAdditionalCharge)
