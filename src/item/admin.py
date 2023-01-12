from django.contrib import admin

from .models import Item, ItemCategory, PackingType, Unit, Manufacturer, GenericName, PackingTypeDetail


# Register your models here.

class ManufacturerAdminModel(admin.ModelAdmin):
    model = Manufacturer
    ordering = ('id',)
    list_display = ('id', 'name', 'active')


class GenericNameAdminModel(admin.ModelAdmin):
    model = GenericName
    ordering = ('id',)
    list_display = ('id', 'name', 'active')


class ItemAdminModel(admin.ModelAdmin):
    model = Item
    search_fields = ('name', 'code')
    list_filter = ('name', 'code')
    ordering = ('id',)
    list_display = ('id', 'name', 'location', 'active')


admin.site.register(Unit)
admin.site.register(Manufacturer, ManufacturerAdminModel)
admin.site.register(GenericName, GenericNameAdminModel)
admin.site.register(Item, ItemAdminModel)
admin.site.register(ItemCategory)
admin.site.register(PackingType)
admin.site.register(PackingTypeDetail)
