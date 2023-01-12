from django.contrib import admin

from .models import OrderMaster, OrderDetail


class OrderDetailInline(admin.StackedInline):
    model = OrderDetail


class OrderMasterAdmin(admin.ModelAdmin):
    inlines = [OrderDetailInline, ]
    list_display = ['id', 'order_no', 'status']
    search_fields = ['id']


class OrderDetailFilterAdmin(admin.ModelAdmin):
    search_fields = ['id']


# Register your models here.
admin.site.register(OrderDetail, OrderDetailFilterAdmin)
admin.site.register(OrderMaster, OrderMasterAdmin)
