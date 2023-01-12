from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.db import connection, connections
from django.shortcuts import render
from django.urls import path

from .models import CustomGroup, CustomPermission, PermissionCategory


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

class PermissionInlineModelAdmin(admin.TabularInline):
    model = CustomPermission

class PermissionCategoryAdmin(admin.ModelAdmin):
    model = PermissionCategory
    search_fields = ('name',)
    inlines = [PermissionInlineModelAdmin]
    list_display = ('id', 'name', 'created_date_ad',  'created_date_bs', 'created_by')
    
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/',self.upload_csv),]
        return new_urls + urls


    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_upload']
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
            print(len(csv_data))
            # print("data of csv")
            with connection.cursor() as cursor:
                for data in csv_data:
                    # print('data: ', data)
                    fields = data.split(",")
                    # connections['default'].cursor().execute(f"SET search_path to customer1")
                    cursor.execute(f'''insert into user_group_permissioncategory values( {fields[0]}, '{fields[1]}', '{fields[2]}' , '{fields[3]}', {fields[4]} );''')

        form = CsvImportForm()
        data = {"form":form}
        return render(request, "admin/user_group/permissioncategory/csv_upload.html", data)


class PermissionAdmin(admin.ModelAdmin):
    model = CustomPermission
    search_fields = ('code_name',)
    list_display = ('id', 'name','code_name', 'category','created_date_ad',  'created_date_bs', 'created_by')
    

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/',self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_upload']
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
            print(len(csv_data))
            # print("data of csv")
            with connection.cursor() as cursor:
                for data in csv_data:
                    # print('data: ', data)
                    fields = data.split(",")
                    # connections['default'].cursor().execute(f"SET search_path to customer1")
                    cursor.execute(f'''insert into user_group_custompermission values( {fields[0]}, '{fields[1]}', '{fields[2]}' , '{fields[3]}', '{fields[4]}', {fields[5]}, {fields[6]});''')

        form = CsvImportForm()
        data = {"form":form}
        return render(request,"admin/user_group/custompermission/csv_upload.html", data)

admin.site.unregister(Group)
admin.site.register(CustomGroup)
admin.site.register(CustomPermission, PermissionAdmin)
admin.site.register(PermissionCategory, PermissionCategoryAdmin)
