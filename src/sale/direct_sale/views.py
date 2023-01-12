from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F
from django.db.models import Max
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from src.core_app.models import OrganizationSetup
from src.item.models import Item
from src.item_serialization.models import PackingTypeDetailCode
from src.item_serialization.services.pack_and_serial_info import find_available_serial_no
from src.purchase.models import PurchaseDetail
from .serializers import SaveDirectSaleMasterSerializer
from ..models import SaleMaster
from ..sale_permissions import DirectSalePermission
from ..sale_unique_id_generator import generate_sale_no


class DirectSaleSerialNoInfoView(APIView):

    def get(self, request, code, *args, **kwargs):
        if find_available_serial_no(serial_no=code):
            serial_no = PackingTypeDetailCode.objects.filter(
                ref_packing_type_detail_code__isnull=True
            ).annotate(
                pack_type_code_code=F('pack_type_code__code'),
                purchase_detail_id=F('pack_type_code__purchase_detail_id'),
                batch_no=F("pack_type_code__purchase_detail__batch_no")
            ).get(code=code)
            return Response(serial_no, status=status.HTTP_200_OK)
        else:
            return Response({"error": "provided serial no not available in the inventory"},
                            status=status.HTTP_404_NOT_FOUND)


class SaveDirectSaleApiView(CreateAPIView):
    serializer_class = SaveDirectSaleMasterSerializer
    queryset = SaleMaster.objects.all()
    permission_classes = [DirectSalePermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if OrganizationSetup.objects.first() is None:
            return Response({'organization setup': 'Please insert Organization setup before making any sale'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data["sale_no"] = generate_sale_no(1)
        request.data["sale_type"] = 1

        serializer = SaveDirectSaleMasterSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # send data to IRD
            # sale_master_id = purchase_order_serializer.data['id']
            # ird_thread = threading.Thread(target=save_data_to_ird, args=(sale_master_id, request), kwargs={})
            # ird_thread.setDaemon = True
            # ird_thread.start()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemCostApiView(APIView):

    def get(self, request, pk):
        try:
            item = Item.objects.get(id=pk)
            highest_sale_cost = PurchaseDetail.objects.filter(item_id=item.id).values('item').annotate(
                highest_sale_cost=Max("sale_cost"),
                item_name=F('item__name'),
                item_id=F('item_id'), item_category=F('item__item_category'),
                taxable=F('item__taxable'),
                discountable=F('item__discountable')

            ).values("highest_sale_cost", "item_name", "item_id", "item_category", "taxable", "discountable")
            if highest_sale_cost:
                return Response(highest_sale_cost, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"batch with item id {pk} does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": f"item id {pk} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
