from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Location


# Register your models here.

class LocationMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20


admin.site.register(Location, LocationMPTTModelAdmin, list_display=(
    'id',
    'name',
    'level',
    'code'
    # 'indented_title',
    # ...more fields if you feel like it...
), )
