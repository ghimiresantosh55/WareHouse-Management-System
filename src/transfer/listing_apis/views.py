from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView

from src.item.models import PackingTypeDetail
from src.transfer.listing_apis.serializers import TransferItemPackingTypeListSerializer


class TransferItemPackingTypeListApiView(ListAPIView):
    queryset = PackingTypeDetail.objects.filter(active=True)
    serializer_class = TransferItemPackingTypeListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['id', 'item']
    ordering_fields = ['id', 'created_date_ad']
    search_fields = ['packing_type__name']
