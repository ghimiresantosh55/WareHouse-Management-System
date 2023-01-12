from django.contrib import admin
from .models import QuotationMaster, QuotationDetail

admin.site.register(QuotationMaster)
admin.site.register(QuotationDetail)