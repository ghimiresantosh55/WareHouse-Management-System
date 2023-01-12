from django.contrib import admin
from .models import PPBMain, PPBDetail, TaskMain, TaskDetail

admin.site.register(PPBMain)
admin.site.register(PPBDetail)
admin.site.register(TaskMain)
admin.site.register(TaskDetail)

