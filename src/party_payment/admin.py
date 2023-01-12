from django.contrib import admin
from .models import PartyPayment, PartyPaymentDetail, BasicPartyPayment, BasicPartyPaymentDetail
# Register your models here.

class PartyPaymentDetailAdmin(admin.ModelAdmin):
    list_display=['id']


admin.site.register(PartyPaymentDetail,PartyPaymentDetailAdmin)
admin.site.register(PartyPayment)
admin.site.register(BasicPartyPayment)
admin.site.register(BasicPartyPaymentDetail)