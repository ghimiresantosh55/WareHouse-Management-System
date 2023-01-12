
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from src.sale.models import SaleMaster, SaleDetail
from.serializers import SaleMasterListSerializer, SaleDetailListSerializer
from rest_framework.generics import  RetrieveAPIView
from src.repair.models import Repair
from .serializers import RepairListSerializer

class SaleMasterListFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
    item = django_filters.NumberFilter(field_name='sale_details__item', distinct=True)

    class Meta:
        model = SaleMaster
        fields = ['id', 'customer', 'sale_no','item', 'date',]

class SaleMasterListApiView(ListAPIView):
    queryset = SaleMaster.objects.filter(active=True)
    serializer_class = SaleMasterListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_class = SaleMasterListFilterSet
    search_fields = ['sale_no','id','customer__first_name','customer__last_name']
    ordering_fields = ['id', ]


class SaleDetailListFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
  
    class Meta:
        model = SaleDetail
        fields = ['id', 'sale_master','sale_master__customer', 'item', 'date',]

class SaleDetailListApiView(ListAPIView):
    queryset = SaleDetail.objects.all()
    serializer_class = SaleDetailListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_class =  SaleDetailListFilterSet
    search_fields = ['id','item__name','sale_master__customer__first_name']
    ordering_fields = ['id', ]



class RepairSummaryViewSet(RetrieveAPIView):
    queryset = Repair.objects.all().prefetch_related('repair_details') 
    serializer_class = RepairListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = search_filter
    ordering_fields = common_filter
    filterset_fields = common_filter
