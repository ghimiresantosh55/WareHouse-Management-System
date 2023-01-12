import django_filters
from django.db import transaction
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from src.item_serialization.models import PackingTypeCode
from src.purchase.models import PurchaseDetail
from src.purchase.models import PurchaseMaster
from .location_serializers import GetLocationPurchaseDetailsSerializer, UpdateLocationPurchaseDetailSerializer
from .opening_stock_permissions import OpeningStockPermission
from .serializers import OpeningStockSerializer, SaveOpeningStockSerializer, UpdateOpeningStockSerializer, \
    OpeningStockSummarySerializer


class OpeningStockFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
    item = django_filters.NumberFilter(field_name='purchase_details__item', distinct=True)

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'date', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier', 'item']


# date supplier item created_at
# Create your views here.
class OpeningStockViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [OpeningStockPermission]
    # we need to display only opening stock so purchase_type=3
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = OpeningStockSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'purchase_details__item__name', 'purchase_no', 'supplier__name', 'grand_total']
    ordering_fields = ['id']
    filter_class = OpeningStockFilterSet


# for patch operation
class OpeningStockSummaryViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [OpeningStockPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = OpeningStockSummarySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'purchase_details__item__name']
    ordering_fields = ['id']
    filter_fields = ['id', 'purchase_details__item__name']


class SaveOpeningStockView(viewsets.ModelViewSet):
    permission_classes = [OpeningStockPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = SaveOpeningStockSerializer
    http_method_names = ['post']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = SaveOpeningStockSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# performing of patch operation for Opening Stock
class UpdateOpeningStockViewset(viewsets.ModelViewSet):
    permission_classes = [OpeningStockPermission]
    queryset = PurchaseMaster.objects.filter(purchase_type=3)
    serializer_class = UpdateOpeningStockSerializer
    http_method_names = ['patch']

    # we are allowed to perform patch operation in purchase_type=3 only 
    def get_purchase_master(self, pk):
        try:
            return PurchaseMaster.objects.get(id=pk, purchase_type=3)
        except PurchaseMaster.DoesNotExist:
            return False

    @transaction.atomic
    def partial_update(self, request, pk):
        purchase_master = self.get_purchase_master(pk)

        # checking if the purchase_master have value or not
        if purchase_master is not False:

            try:
                if request.data['grand_total'] == "":
                    request.data['grand_total'] = None
            except KeyError:
                return Response({'key_error': 'please provide grand_total Keys'},
                                status=status.HTTP_400_BAD_REQUEST)

            opening_stock_serializer = UpdateOpeningStockSerializer(purchase_master, data=request.data, partial=True,
                                                                    context={'request': request})

            if opening_stock_serializer.is_valid(raise_exception=True):
                opening_stock_serializer.save()
                return Response(opening_stock_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(opening_stock_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(data="To perform patch operation value for purchase_type must be 3",
                        status=status.HTTP_404_NOT_FOUND)


class UpdateLocationPurchaseDetailView(ListCreateAPIView):
    queryset = PurchaseDetail.objects.filter(purchase__purchase_type=3).distinct().prefetch_related(
        Prefetch('pu_pack_type_codes',
                 queryset=PackingTypeCode.objects.order_by('id').select_related('location'))
    ).select_related('item',
                     'item_category',
                     'packing_type')
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['purchase', 'item', 'item_category', 'id']

    def get_serializer_class(self):
        serializer_class = GetLocationPurchaseDetailsSerializer
        if self.request.method == 'POST':
            serializer_class = UpdateLocationPurchaseDetailSerializer

        return serializer_class

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
