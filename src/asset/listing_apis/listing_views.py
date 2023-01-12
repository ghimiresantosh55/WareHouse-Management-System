import django_filters
from django.db.models import F, Count
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from src.item.models import Item
from src.item_serialization.models import PackingTypeDetailCode
from src.purchase.models import PurchaseDetail
from .listing_serializers import AssetSerialNoInfoListSerializer, AssetItemLIstSerializer


class SerialNoInfoView(RetrieveAPIView):
    queryset = PackingTypeDetailCode.objects.all()
    serializer_class = AssetSerialNoInfoListSerializer

    def retrieve(self, request, *args, **kwargs):
        pack_type_detail_code = kwargs.get("serial_no")
        pack_type_detail_code_available = PackingTypeDetailCode.objects.filter(
            assetlist__isnull=True,
            code=pack_type_detail_code,
            packingtypedetailcode__isnull=True
        ).annotate(
            ref_count=Count('pack_type_detail_code_of_sale') % 2
        ).filter(ref_count=0).exists()
        if not pack_type_detail_code_available:
            return Response({'message': 'This serial no is already sold or added to Asset'})

        try:

            data = PackingTypeDetailCode.objects.annotate(
                supplier_name=F('pack_type_code__purchase_detail__purchase__supplier__name'),
                item_name=F('pack_type_code__purchase_detail__item__name'),
                purchase_no=F('pack_type_code__purchase_detail__purchase__purchase_no'),
                bill_no=F('pack_type_code__purchase_detail__purchase__bill_no'),
                item_category_name=F('pack_type_code__purchase_detail__item_category__name'),
                purchase_detail_id=F('pack_type_code__purchase_detail__id'),
                manufacturer=F('pack_type_code__purchase_detail__item__manufacturer__name')
            ).values(
                "id", "code", "supplier_name",
                "item_name", "purchase_no", "bill_no", "item_category_name",
                'manufacturer', 'purchase_detail_id'
            ).get(code=pack_type_detail_code)
            if data['purchase_no'] is None:
                return Response({"serial_no": "Is not verified"}, status=status.HTTP_400_BAD_REQUEST)
            purchase_detail_id = PurchaseDetail.objects.get(id=data['purchase_detail_id'])
            data['related_codes'] = PackingTypeDetailCode.objects.filter(
                pack_type_code__purchase_detail__id=purchase_detail_id.id,
                assetlist__isnull=True,
                packingtypedetailcode__isnull=True
            ).annotate(
                ref_count=Count('pack_type_detail_code_of_sale') % 2
            ).filter(ref_count=0).values('id', 'code').distinct()

            return Response(data, status=status.HTTP_200_OK)
        except PackingTypeDetailCode.DoesNotExist:
            return Response({"serial_no": "does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class FilterForAssetItem(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = Item
        fields = ['id', 'name', 'item_category', 'purchase_cost', 'packing_type_details__packing_type']


class AssetItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(fixed_asset=True)
    serializer_class = AssetItemLIstSerializer
    filter_class = FilterForAssetItem
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'name']
    ordering_fields = ['id', ]
    http_method_names = ['get', ]