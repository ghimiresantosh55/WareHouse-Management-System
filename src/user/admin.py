from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# imported model here

# Register your models here.
class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email', 'user_name',)
    list_filter = ('email', 'user_name', 'first_name', 'is_active', 'is_staff')
    ordering = ('-created_date_ad',)
    list_display = ('id', 'user_name', 'email', 'is_active', 'is_staff')
    fieldsets = (
        (None,
         {'fields': ('email', 'user_name', 'password', 'gender', 'birth_date', 'groups', 'photo', 'created_date_ad',
                     'created_date_bs', 'first_name', 'last_name', 'full_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'password1', 'password2', 'groups', 'is_active', 'created_date_ad',
                       'created_date_bs', 'is_staff', 'gender', 'birth_date', 'created_by', 'photo')}
         ),
    )


admin.site.register(User, UserAdminConfig)
