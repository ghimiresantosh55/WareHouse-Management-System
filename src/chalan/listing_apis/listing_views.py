from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.customer.models import Customer
from .listing_serializers import CustomerChalanListSerializer, ChalanNoSerializer
from ..chalan_permissions import ChalanPermission
from ..models import ChalanMaster


class CustomerListApiView(ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerChalanListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'middle_name', 'last_name', 'pan_vat_no']
    ordering_fields = ['id', 'first_name']


class ChalanNoListAPIView(ListAPIView):
    permission_classes = [ChalanPermission]
    serializer_class = ChalanNoSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'chalan_no']
    ordering_fields = ['id']
    filter_fields = ['id', 'chalan_no']

    def get_queryset(self):
        return ChalanMaster.objects.filter(status=1,
                                           chalanmaster__status=3).values('id', 'chalan_no')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
