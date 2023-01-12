from django.contrib import admin

from .models import (AdditionalChargeType, AppAccessLog, Bank, BankDeposit, Country, DiscountScheme,
                     District, FiscalSessionAD, FiscalSessionBS, OrganizationRule, OrganizationSetup,
                     PaymentMode, Province, Store, Currency)

# Register your models here.
# Register your models here.

admin.site.register(Country)
admin.site.register(Province)
admin.site.register(Currency)
admin.site.register(District)
admin.site.register(OrganizationRule)
admin.site.register(OrganizationSetup)
admin.site.register(Bank)
admin.site.register(BankDeposit)
admin.site.register(PaymentMode)
admin.site.register(DiscountScheme)
admin.site.register(AdditionalChargeType)
admin.site.register(AppAccessLog)
admin.site.register(Store)
admin.site.register(FiscalSessionAD)
admin.site.register(FiscalSessionBS)
