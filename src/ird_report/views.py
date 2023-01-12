from django.db import models
from django.db.models.expressions import F
from django.db.models import Count
from django.shortcuts import render
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

# model
from src.sale.models import SaleMaster, SalePrintLog

# serializer
from .serializers import UserActivityLogSerializer, IRDLogSerializer, MaterialViewReportSerializer

from src.custom_lib.functions.fiscal_year import get_fiscal_year
# permission
from .ird_report_permissions import ReportMaterializedPermission, UserActivityLogPermission

# query
from django.db.models.functions.comparison import Cast
from django.db.models import fields, F, Q


# Create your views here.
class MaterialViewReportViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReportMaterializedPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = MaterialViewReportSerializer
    http_method_names = ['get', 'head']

    def list(self, request, **kwargs):
        query_dict = {}
        for k, vals in request.GET.lists():
            print(k, vals[0])
            if vals[0] != '':
                k = str(k)
                query_dict[k] = vals[0]
        sale_master_id_list = set(SalePrintLog.objects.values_list('sale_master', flat=True))
        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        # using set avoid duplicate value
        sale_master_id_list = set(SaleMaster.objects.filter(**query_filter).values_list('id', flat=True))

        # defining list
        required_data = []

        for sale_master_id in sale_master_id_list:
            # user related_field name for accessing child from parent 
            required_data.append(SaleMaster.objects.filter(id=sale_master_id). \
                                 earliest('sale_masters'))

        output_serializer = MaterialViewReportSerializer(required_data, many=True)

        # fiscal year
        for fiscal in range(len(output_serializer.data)):
            # bill_date is converted into string 
            fiscal_year_code = get_fiscal_year(str(output_serializer.data[fiscal]['bill_date']))[
                'short_fiscal_session_bs']
            output_serializer.data[fiscal]['fiscal_year'] = fiscal_year_code
        # print(output_serializer.data[0]['fiscal_year']
        # a =output_serializer.data.filter(**query_filter)

        page = self.paginate_queryset(output_serializer.data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserActivityLogReportViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [UserActivityLogPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = UserActivityLogSerializer
    http_method_names = ['get', 'head']

    def list(self, request):
        query_dict = {}
        order_dict = {}
        # print(request.GET.lists())
        for k, vals in request.GET.lists():
            if str(k) == "ordering":
                order_dict[k] = vals[0]
                # print(vals[0])
            else:
                if vals[0] != '':
                    k = str(k)
                    query_dict[k] = vals[0]
        # print(order_dict.values())
        if not order_dict:
            order_dict['ordering'] = "transaction_date"

        query_filter = {}
        if "date_after" in query_dict:
            query_filter['created_date_ad__date__gte'] = query_dict['date_after']
        if "date_before" in query_dict:
            query_filter['created_date_ad__date__lte'] = query_dict['date_before']

        ird_data = SaleMaster.objects.filter(**query_filter).values('created_date_ad__date'). \
            annotate(
            username=F('created_by__user_name'),
            first_name=F('created_by__first_name'),
            middle_name=F('created_by__middle_name'),
            last_name=F('created_by__last_name'),
            transaction_date=Cast("created_date_ad", fields.DateField()),
            sale_type=F('sale_type'),
            total_activity=Count('id')). \
            values(
            'username', 'first_name', 'middle_name', 'last_name', 'transaction_date',
            'sale_type', 'total_activity'
        ).order_by(order_dict['ordering'])

        for query in ird_data:
            query['sale_type'] = ird_data.model(sale_type=query['sale_type']).get_sale_type_display()

        page = self.paginate_queryset(ird_data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(ird_data, status=status.HTTP_200_OK)

