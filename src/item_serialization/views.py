from django.db import transaction
from django.db.models import Count
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PackingTypeCode, PackingTypeDetailCode
from .serialization_permissions import UpdatePacketLocationPermission, PacketInfoPermission
from .serializers import (PackTypeCodeLocationSerializer,
                          PackTypeCodeInfoSerializer,
                          UpdatePackTypeLocationSerializer, PackCodeDetailInfoSerializer)


class PackLocationRetrieveApiView(RetrieveAPIView):
    queryset = PackingTypeCode.objects.all()
    serializer_class = PackTypeCodeLocationSerializer
    permission_classes = [PacketInfoPermission]

    def retrieve(self, request, *args, **kwargs):
        pack_code = kwargs.get('pack_code')
        try:
            pack_code_data = PackingTypeCode.objects.get(code=pack_code)
        except PackingTypeCode.DoesNotExist:
            return Response({"pk": f"{pack_code} does not exist"}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(pack_code_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePackTypeCodeLocationApiView(CreateAPIView):
    serializer_class = UpdatePackTypeLocationSerializer
    permission_classes = [UpdatePacketLocationPermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(UpdatePackTypeCodeLocationApiView, self).create(request, args, kwargs)


class PackTypeInfoRetrieveApiView(RetrieveAPIView):
    serializer_class = PackTypeCodeInfoSerializer
    queryset = PackingTypeCode.objects.all()
    permission_classes = [PacketInfoPermission]

    def retrieve(self, request, *args, **kwargs):
        pack_code = kwargs.get('pack_code')
        try:
            pack_code_data = PackingTypeCode.objects.prefetch_related(
                Prefetch(
                    'pack_type_detail_codes',
                    queryset=PackingTypeDetailCode.objects.filter(
                        assetlist__isnull=True,
                        packingtypedetailcode__isnull=True
                    ).annotate(
                        ref_count=Count('pack_type_detail_code_of_sale') % 2
                    ).filter(ref_count=0)
                )
            ).select_related(
                'purchase_detail__item', 'location'
            ).get(code=pack_code)
        except PackingTypeCode.DoesNotExist:
            return Response({"pk": f"{pack_code} does not exist"}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(pack_code_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.exceptions import ValidationError


class PackCodeDetailInfoRetrieveView(APIView):
    queryset = PackingTypeDetailCode.objects.filter(ref_packing_type_detail_code__isnull=True)
    serializer_class = PackCodeDetailInfoSerializer

    def get_object(self, item_serial_no):
        try:
            packing_type_detail_code = PackingTypeDetailCode.objects.get(code=item_serial_no)
        except PackingTypeDetailCode.DoesNotExist:
            raise ValidationError({"error": "code does not exist"})
        return packing_type_detail_code

    def get(self, request, item_serial_no_code, *args, **kwargs):
        packing_type_detail_code = self.get_object(item_serial_no_code)
        serializer = self.serializer_class(packing_type_detail_code)
        return Response(serializer.data, status=status.HTTP_200_OK)
