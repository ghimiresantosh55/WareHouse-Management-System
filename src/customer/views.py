# third-party
import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

# importing permission
from .customer_permissions import CustomerPermission
# imported models
from .models import Customer
# imported serializer
from .serializers import CustomerSerializer

# for history report
from ..user_group.models import CustomPermission


class FilterForCustomer(django_filters.FilterSet):
    # for date range filter after_date and before_date
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    # iexact is used for Case-insensitive exact match in search field. Nepal and nEpaL are same
    name = django_filters.CharFilter(lookup_expr='iexact')
    address = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Customer
        fields = ['phone_no', 'active', 'id', 'pan_vat_no']


class CustomerViewSet(viewsets.ModelViewSet):
    # permission
    permission_classes = [CustomerPermission]
    queryset = Customer.objects.all().select_related("country")
    serializer_class = CustomerSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForCustomer
    search_fields = ['first_name', 'last_name', 'address', 'id', 'pan_vat_no']
    ordering_fields = ['first_name', 'id', 'pan_vat_no']
    http_method_names = ['get', 'head', 'post', 'patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if self.request.method == 'GET':
            if self.request.user.is_superuser:
                return Customer.objects.all().select_related('country')
            else:
                try:
                    groups = self.request.user.groups.filter(is_active=True).values_list('id', flat=True)
                    user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                        'code_name', flat=True
                    )
                    if 'view_customer' in user_permissions:
                        return Customer.objects.all().select_related('country')
                    elif 'self_customer' in user_permissions:
                        return Customer.objects.filter(created_by=self.request.user).select_related('country')
                    return Response(status=status.HTTP_403_FORBIDDEN)
                except:
                    return Response(status=status.HTTP_403_FORBIDDEN)
        return Customer.objects.all().select_related("country")
