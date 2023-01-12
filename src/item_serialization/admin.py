from django.contrib import admin

from .models import (PackingTypeCode, PackingTypeDetailCode,
                     SalePackingTypeCode, SalePackingTypeDetailCode, RfidTag)


# Register your models here.


class InlinePackingTypeDetailCode(admin.TabularInline):
    model = PackingTypeDetailCode


class InlineSalePckTypeDetailCode(admin.TabularInline):
    model = SalePackingTypeDetailCode


class SalePackingTypeAdmin(admin.ModelAdmin):
    inlines = [InlineSalePckTypeDetailCode]


class PackingTypeCodeModel(admin.ModelAdmin):
    inlines = [InlinePackingTypeDetailCode]


admin.site.register(PackingTypeCode, PackingTypeCodeModel)
admin.site.register(RfidTag)
admin.site.register(PackingTypeDetailCode)
admin.site.register(SalePackingTypeDetailCode)
admin.site.register(SalePackingTypeCode, SalePackingTypeAdmin)
