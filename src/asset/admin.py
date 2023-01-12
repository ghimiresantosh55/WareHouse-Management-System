from django.contrib import admin

from .models import AssetIssue, Asset, AssetService, AssetCategory, AssetSubCategory
from .models import AssetList


@admin.register(AssetList)
class AssetListModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'packing_type_detail_code']


admin.site.register(AssetIssue)
admin.site.register(AssetService)
admin.site.register(Asset)
admin.site.register(AssetCategory)
admin.site.register(AssetSubCategory)
