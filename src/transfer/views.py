import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response

from src.core_app.models import OrganizationSetup
from src.transfer.models import TransferMaster, TransferDetail, TransferOrderMaster, TransferOrderDetail
from src.transfer.serializers import SaveTransferMasterSerializer, TransferMasterListSerializer, \
    TransferDetailListSerializer, SaveTransferOrderMasterSerializer, TransferOrderMasterListSerializer, \
    TransferOrderDetailListSerializer, PickupTransferDetailSerializer, TransferSummarySerializer, \
    TransferToBranchSerializer, CancelTransferDetailSerializer, CancelTransferMasterSerializer, \
    UpdateTransferSerializer, UpdateTransferDetailSerializer
from src.transfer.transfer_permissions import TransferPermission, TransferOrderPermission, \
    CancelTransferOrderPermission, PickupTransferOrderPermission
from src.transfer.transfer_unique_id_generator import generate_transfer_no, generate_transfer_order_no


# Create your views here.
class SaveTransferApiView(CreateAPIView):
    serializer_class = SaveTransferMasterSerializer
    queryset = TransferMaster.objects.all()
    permission_classes = [TransferOrderPermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if OrganizationSetup.objects.first() is None:
            return Response({'organization setup': 'Please insert Organization setup before making any sale'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data["transfer_no"] = generate_transfer_no(1)
        request.data["transfer_type"] = 1

        serializer = SaveTransferMasterSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # save_transfer_data_to_branch(request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilterForTransferMasterList(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    item = django_filters.NumberFilter(field_name='transfer_details__item', label='item')

    class Meta:
        model = TransferMaster
        fields = ['id', 'transfer_no', 'date', 'branch', 'item']


class TransferMasterListViewSet(ListAPIView):
    permission_classes = [TransferOrderPermission]
    queryset = TransferMaster.objects.all()
    serializer_class = TransferMasterListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = FilterForTransferMasterList
    ordering_fields = ['id', 'created_date_ad', 'transfer_no']
    search_fields = ['transfer_no']


class TransferDetailListViewSet(ListAPIView):
    permission_classes = [TransferOrderPermission]
    queryset = TransferDetail.objects.all()
    serializer_class = TransferDetailListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['id', 'transfer_master']
    ordering_fields = ['id', 'created_date_ad']


class SaveTransferOrderApiView(CreateAPIView):
    serializer_class = SaveTransferOrderMasterSerializer
    queryset = TransferOrderMaster.objects.all()
    permission_classes = [TransferOrderPermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if OrganizationSetup.objects.first() is None:
            return Response({'organization setup': 'Please insert Organization setup before making any sale'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data["transfer_order_no"] = generate_transfer_order_no()

        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferOrderMasterListViewSet(ListAPIView):
    permission_classes = [TransferOrderPermission]
    queryset = TransferOrderMaster.objects.all()
    serializer_class = TransferOrderMasterListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['id', 'created_date_ad']
    search_fields = ['transfer_order_no']


class TransferOrderDetailListViewSet(ListAPIView):
    permission_classes = [TransferOrderPermission]
    queryset = TransferOrderDetail.objects.all()
    serializer_class = TransferOrderDetailListSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['id', 'transfer_order_master']
    ordering_fields = ['id', 'created_date_ad']


class PickupTransferDetailViewSet(CreateAPIView):
    permission_classes = [PickupTransferOrderPermission]
    serializer_class = PickupTransferDetailSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(PickupTransferDetailViewSet, self).create(request, *args, **kwargs)


class TransferSummaryApiView(RetrieveAPIView):
    permission_classes = [TransferOrderPermission]
    serializer_class = TransferSummarySerializer
    queryset = TransferMaster.objects.all()


class TransferToBranchCreateViewSet(CreateAPIView):
    permission_classes = [TransferPermission]
    serializer_class = TransferToBranchSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(TransferToBranchCreateViewSet, self).create(request, *args, **kwargs)


class CancelTransferDetailView(CreateAPIView):
    permission_classes = [TransferOrderPermission]
    serializer_class = CancelTransferDetailSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(CancelTransferDetailView, self).create(request, *args, **kwargs)


class CancelTransferMasterView(CreateAPIView):
    permission_classes = [CancelTransferOrderPermission]
    serializer_class = CancelTransferMasterSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(CancelTransferMasterView, self).create(request, *args, **kwargs)


class UpdateTransferApiView(UpdateAPIView):
    permission_classes = [TransferOrderPermission]
    queryset = TransferMaster.objects.filter(transfer_type=1,
                                             is_transferred=False)
    serializer_class = UpdateTransferSerializer
    http_method_names = ['patch']

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        # update old tranfer_details
        all_transfer_details = request.data.pop("transfer_details")

        # save purchase order details
        transfer_details_create = []
        for transfer_detail in all_transfer_details:
            if transfer_detail.get("id", False):

                transfer_detail_instance = TransferDetail.objects.get(id=transfer_detail['id'])
                transfer_detail_update_serializer = UpdateTransferDetailSerializer(
                    transfer_detail_instance, data=transfer_detail, partial=True
                )
                if transfer_detail_update_serializer.is_valid(raise_exception=True):
                    transfer_detail_update_serializer.save()
                else:
                    return Response(transfer_detail_update_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                transfer_details_create.append(transfer_detail)

        request.data['transfer_details'] = transfer_details_create
        return super(UpdateTransferApiView, self).partial_update(request, *args, **kwargs)

# class TenantMapView(ListAPIView):
#     permission_classes = [TransferPermission]
#     queryset = Tenant.objects.all()
#
#     def list(self, request, *args, **kwargs):
#         connection.cursor().execute(f"SET search_path to public")
#
#         queryset = self.filter_queryset(Tenant.objects.all())
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = TenantSerializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
