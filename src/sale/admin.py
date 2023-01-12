from django.contrib import admin
from .models import SaleMaster, SaleDetail, SalePaymentDetail, SaleAdditionalCharge ,SalePrintLog


class SaleDetailInline(admin.TabularInline):
     model = SaleDetail
class SaleMasterAdmin(admin.ModelAdmin):
     inlines = [SaleDetailInline]
     list_display =('id','sale_no','sale_type','grand_total','pay_type','created_date_ad')

class SaleDetailAdmin(admin.ModelAdmin):
     list_display =('id','sale_master','item','net_amount','ref_purchase_detail','ref_sale_detail','ref_order_detail','created_date_ad')

class SalePaymentDetailAdmin(admin.ModelAdmin):
     list_display =('id','sale_master','payment_mode','amount','created_date_ad')

class SaleAdditionalChargeAdmin(admin.ModelAdmin):
     list_display =('id','charge_type','sale_master','amount','created_date_ad')

admin.site.register(SaleMaster, SaleMasterAdmin)
admin.site.register(SaleDetail, SaleDetailAdmin)
admin.site.register(SalePaymentDetail, SalePaymentDetailAdmin)
admin.site.register(SaleAdditionalCharge, SaleAdditionalChargeAdmin)
admin.site.register(SalePrintLog)