from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from src.core_app.models import Bank, Country
from .listing_serializers import BankBankDepositSerializer, CountryOrganizationSetupListSerializer
from ..core_app_permissions import SystemSetupPermission


class CountryListApiView(ListAPIView):
    permission_classes = [SystemSetupPermission]
    queryset = Country.objects.filter(active=True)
    serializer_class = CountryOrganizationSetupListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']


class BankListApiView(ListAPIView):
    permission_classes = [SystemSetupPermission]
    queryset = Bank.objects.filter(active=True)
    serializer_class = BankBankDepositSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']
