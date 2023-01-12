from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response

from src.department_transfer.serializers import SaveDepartmentTransferMasterSerializer, \
    DepartmentTransferMasterListSerializer, DepartmentTransferMasterSummarySerializer, \
    CancelDepartmentTransferDetailSerializer, CancelDepartmentTransferMasterSerializer, \
    UpdateDepartmentTransferMasterSerializer, UpdateDepartmentTransferDetailSerializer, \
    DepartmentTransferDetailListSerializer, ApproveDepartmentTransferMasterSerializer, \
    PickupDepartmentTransferDetailSerializer

from .models import DepartmentTransferMaster, DepartmentTransferDetail
from .department_transfer_permissions import CrateDepartmentTransferPermission, ViewDepartmentTransferPermission, \
    UpdateDepartmentTransferPermission, ApproveDepartmentTransferPermission


class DepartmentTransferCreateApiView(CreateAPIView):
    queryset = DepartmentTransferMaster.objects.all()
    serializer_class = SaveDepartmentTransferMasterSerializer
    permission_classes = [CrateDepartmentTransferPermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(DepartmentTransferCreateApiView, self).create(request)


class DepartmentTransferMasterListViewSet(ListAPIView):
    queryset = DepartmentTransferMaster.objects.all()
    serializer_class = DepartmentTransferMasterListSerializer
    permission_classes = [ViewDepartmentTransferPermission]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'created_date_ad']
    filterset_fields = ['from_department', 'to_department', 'is_approved']


class DepartmentTransferMasterToListViewSet(ListAPIView):
    queryset = DepartmentTransferMaster.objects.all()
    serializer_class = DepartmentTransferMasterListSerializer
    permission_classes = [ViewDepartmentTransferPermission]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'created_date_ad']
    filterset_fields = ['from_department', 'to_department', 'is_approved']

    def get_queryset(self):
        departments = self.request.user.departments.all().values_list('id', flat=True)
        queryset = DepartmentTransferMaster.objects.filter(to_department__in=departments)
        return queryset


class DepartmentTransferMasterFromListViewSet(ListAPIView):
    queryset = DepartmentTransferMaster.objects.all()
    serializer_class = DepartmentTransferMasterListSerializer
    permission_classes = [ViewDepartmentTransferPermission]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'created_date_ad']
    filterset_fields = ['from_department', 'to_department', 'is_approved']

    def get_queryset(self):
        departments = self.request.user.departments.all().values_list('id', flat=True)
        queryset = DepartmentTransferMaster.objects.filter(from_department__in=departments)
        return queryset


class DepartmentTransferDetailListViewSet(ListAPIView):
    queryset = DepartmentTransferDetail.objects.all()
    serializer_class = DepartmentTransferDetailListSerializer
    permission_classes = [ViewDepartmentTransferPermission]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['id', 'created_date_ad']
    filterset_fields = ['department_transfer_master']


class DepartmentTransferMasterSummaryViewSet(RetrieveAPIView):
    queryset = DepartmentTransferMaster.objects.all().prefetch_related("department_transfer_details")
    serializer_class = DepartmentTransferMasterSummarySerializer
    permission_classes = [ViewDepartmentTransferPermission]


class CancelDepartmentTransferDetailViewSet(CreateAPIView):
    serializer_class = CancelDepartmentTransferDetailSerializer
    permission_classes = [UpdateDepartmentTransferPermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(CancelDepartmentTransferDetailViewSet, self).create(request)


class CancelDepartmentTransferMasterViewSet(CreateAPIView):
    serializer_class = CancelDepartmentTransferMasterSerializer
    permission_classes = [UpdateDepartmentTransferPermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(CancelDepartmentTransferMasterViewSet, self).create(request)


class ApproveTransferMasterViewSet(CreateAPIView):
    serializer_class = ApproveDepartmentTransferMasterSerializer
    permission_classes = [ApproveDepartmentTransferPermission]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(ApproveTransferMasterViewSet, self).create(request)


class UpdateDepartmentTransferAPIView(UpdateAPIView):
    queryset = DepartmentTransferMaster.objects.filter(is_approved=False, is_received=False, is_cancelled=False)
    serializer_class = UpdateDepartmentTransferMasterSerializer
    http_method_names = ['patch']
    permission_classes = [UpdateDepartmentTransferPermission]

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        department_transfer_details = request.data.pop('department_transfer_details')
        department_transfer_details_create = []
        for department_transfer_detail in department_transfer_details:
            if department_transfer_detail.get("id", False):
                order_detail_instance = DepartmentTransferDetail.objects.get(id=department_transfer_detail['id'])

                serializer = UpdateDepartmentTransferDetailSerializer(
                    order_detail_instance, data=department_transfer_detail, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                department_transfer_details_create.append(department_transfer_detail)

        request.data['department_transfer_details'] = department_transfer_details_create
        return super(UpdateDepartmentTransferAPIView, self).partial_update(request, *args, **kwargs)


class PickupDepartmentTransferDetailApiView(CreateAPIView):
    serializer_class = PickupDepartmentTransferDetailSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = PickupDepartmentTransferDetailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
