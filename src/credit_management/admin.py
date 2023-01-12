from django.contrib import admin
from .models import CreditPaymentDetail, CreditClearance


class CreditClearanceAdmin(admin.ModelAdmin):
     list_display =('id','sale_master','payment_type','receipt_no','total_amount','created_date_ad')
# Register your models here.
admin.site.register(CreditClearance,CreditClearanceAdmin)
admin.site.register(CreditPaymentDetail)