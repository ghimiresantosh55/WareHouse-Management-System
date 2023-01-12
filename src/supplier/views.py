# third-party
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
# imported serializer
from .serializers import SupplierSerializer
import django_filters

# imported models
from .models import Supplier
from .supplier_permissions import SupplierPermission

# for log
from simple_history.utils import update_change_reason


# filter
class FilterForSupplier(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')
    address = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Supplier
        fields = ['phone_no', 'pan_vat_no', 'active']


# viewset for supplier
class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [SupplierPermission]
    queryset = Supplier.objects.all().select_related("country")
    serializer_class = SupplierSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForSupplier
    search_fields = ['name', 'address', 'pan_vat_no']
    ordering_fields = ['id', 'name', 'pan_vat_no']
    http_method_names = ['get', 'head', 'post', 'patch']

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
