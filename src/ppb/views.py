import django_filters
from django.db import transaction
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import UpdateAPIView, CreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response

from .models import PPBMain, PPBDetail, TaskMain, TaskDetail, TaskOutput
from .permissions import PPBPermission, TaskPermission
from .ppb_serializers import (PPBMainListSerializer, PPBMainSummarySerializer, SavePPBMainSerializer,
                              UpdatePPBMainSerializer,
                              UpdatePPBDetailSerializer, PPBDetailDeleteSerializer)
from .task_serializers import SaveTaskMainSerializer, TaskMainSummarySerializer, TaskMainListSerializer, \
    CancelTaskMainSerializer, ApproveTaskMainSerializer, PickupTaskSerializer, SaveTaskOutputSerializer, \
    UpdateTaskSerializer, UpdateTaskDetailSerializer, GetTaskOutputSerializer, GetTaskOutputSummarySerializer


class FilterForPPBMain(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')

    class Meta:
        model = PPBMain
        fields = ['id', 'date', 'ppb_no']


class PPBMainViewSet(viewsets.ModelViewSet):
    permission_classes = [PPBPermission]
    queryset = PPBMain.objects.filter(active=True).prefetch_related(
        Prefetch("ppb_details", queryset=PPBDetail.objects.filter(active=True))
    ).select_related("output_item")
    serializer_class = SavePPBMainSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FilterForPPBMain
    search_fields = ['ppb_no']
    ordering_fields = ['id', 'ppb_no']
    http_method_names = ['post', 'get', 'patch']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdatePPBMainSerializer
        elif self.request.method == 'POST':
            return SavePPBMainSerializer
        else:
            return PPBMainListSerializer

    @action(detail=True, methods=['GET'], url_path="summary")
    def get_ppb_summary(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PPBMainSummarySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(PPBMainViewSet, self).create(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = request.data['remarks']
            if len(remarks) <= 0:
                return Response({"msg": "Please provide at least one word for remarks"},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"msg": "Please provide remarks while updating"}, status=status.HTTP_400_BAD_REQUEST)

        ppb_details = request.data.pop('ppb_details')
        new_ppb_details = []
        for detail in ppb_details:
            if detail.get('id', False):
                ppb_detail_instance = PPBDetail.objects.get(pk=detail['id'])
                update_ppb_detail = UpdatePPBDetailSerializer(ppb_detail_instance, data=detail, partial=True)
                if update_ppb_detail.is_valid(raise_exception=True):
                    update_ppb_detail.save()
                else:
                    return Response(update_ppb_detail.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                new_ppb_details.append(detail)

        request.data['ppb_details'] = new_ppb_details
        return super(PPBMainViewSet, self).partial_update(request, *args, **kwargs)


class DeletePPBDetailAPIView(RetrieveDestroyAPIView):
    queryset = PPBDetail.objects.filter(active=True)
    serializer_class = PPBDetailDeleteSerializer


class FilterForTaskMain(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')

    class Meta:
        model = TaskMain
        fields = ['id', 'date', 'task_no']


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [TaskPermission]
    serializer_class = SaveTaskMainSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FilterForTaskMain
    search_fields = ['task_no']
    ordering_fields = ['id', 'task_no']
    http_method_names = ['post', 'get', 'patch']

    def get_queryset(self):
        if self.request.method == 'PATCH':
            return TaskMain.objects.filter(is_cancelled=False, is_approved=False)
        else:
            return TaskMain.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaveTaskMainSerializer
        elif self.request.method == 'PATCH':
            return UpdateTaskSerializer
        else:
            return TaskMainListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(TaskViewSet, self).create(request, *args, **kwargs)

    @action(detail=True, methods=['GET'], url_path="summary")
    def get_task_summary(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TaskMainSummarySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # validation for not bypassing just in case scenario
        if instance.is_approved:
            return Response({"msg": "This task has already been approved"}, status=status.HTTP_400_BAD_REQUEST)
        if instance.is_cancelled:
            return Response({"msg": "This task has already been cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            remarks = request.data['remarks']
            if len(remarks) <= 0:
                return Response({"msg": "Please provide at least one word for remarks"},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"msg": "Please provide remarks while updating"}, status=status.HTTP_400_BAD_REQUEST)

        task_details = request.data.pop('task_details')
        new_task_details = []
        for detail in task_details:
            if detail.get('id', False):
                task_detail_instance = TaskDetail.objects.get(pk=detail['id'])
                update_task_detail = UpdateTaskDetailSerializer(task_detail_instance, data=detail, partial=True)
                if update_task_detail.is_valid(raise_exception=True):
                    update_task_detail.save()
                else:
                    return Response(update_task_detail.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                new_task_details.append(detail)

        request.data['task_details'] = new_task_details
        return super(TaskViewSet, self).partial_update(request, *args, **kwargs)


class CancelTaskMainAPIView(UpdateAPIView):
    queryset = TaskMain.objects.filter(is_cancelled=False,
                                       is_approved=False)
    serializer_class = CancelTaskMainSerializer

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(CancelTaskMainAPIView, self).partial_update(request, *args, **kwargs)


class CancelSingleTaskDetailAPIView(UpdateAPIView):
    queryset = TaskDetail.objects.filter(is_cancelled=False, task_main__is_approved=False)
    serializer_class = CancelTaskMainSerializer

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(CancelSingleTaskDetailAPIView, self).partial_update(request, *args, **kwargs)


class ApproveTaskMainAPIView(UpdateAPIView):
    queryset = TaskMain.objects.filter(is_cancelled=False, is_approved=False)
    serializer_class = ApproveTaskMainSerializer

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.approved = True
        instance.approved_by = self.request.user
        instance.save()
        return super(ApproveTaskMainAPIView, self).partial_update(request, *args, **kwargs)


class PickupTaskAPIView(CreateAPIView):
    queryset = TaskDetail.objects.all()
    serializer_class = PickupTaskSerializer

    def create(self, request, *args, **kwargs):
        return super(PickupTaskAPIView, self).create(request, *args, **kwargs)


class FilterForTaskOutput(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')

    class Meta:
        model = TaskOutput
        fields = ['id', 'date', 'task_main', 'item']


class TaskOutputViewSet(viewsets.ModelViewSet):
    permission_classes = [TaskPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FilterForTaskOutput
    search_fields = ['item']
    ordering_fields = ['id', 'task_main']
    http_method_names = ['post', 'get']

    def get_queryset(self):
        if self.request.method == 'POST':
            return TaskOutput.objects.all()
        else:
            return TaskOutput.objects.all().prefetch_related(
                Prefetch('task_output', queryset=TaskMain.objects.all().prefetch_related(
                    Prefetch('task_details', queryset=TaskDetail.objects.all())
                ).select_related('department').prefetch_related(
                    Prefetch('ppb_task', queryset=PPBMain.objects.all().prefetch_related(
                        Prefetch('item_ppb', queryset=PPBDetail.objects.all())
                    ))
                ))
            ).select_related('packing_type', 'packing_type_detail', 'item')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaveTaskOutputSerializer
        else:
            return GetTaskOutputSerializer

    @action(detail=True, methods=['GET'], url_path="summary")
    def get_task_output_summary(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GetTaskOutputSummarySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(TaskOutputViewSet, self).create(request, *args, **kwargs)
