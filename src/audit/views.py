# Create your views here
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .audit_no_generator import generate_item_audit_no
from .models import Audit, ItemAudit, ItemAuditDetail
from .serializers import AuditCreateSerializer, AuditReportSerializer, SaveItemAuditSerializer, GetItemAuditSerializer, \
    GetItemAuditSummarySerializer
from ..user_group.models import CustomPermission


class AuditCreateApiView(ModelViewSet):
    queryset = Audit.objects.filter(is_finished=False).prefetch_related("audit_details")
    serializer_class = AuditCreateSerializer
    http_method_names = ['post', 'patch']

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(self, request, *args, **kwargs)


class AuditReportPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser:
            return True

        try:
            groups = request.user.groups.filter(
                is_active=True).values_list('id', flat=True)
            user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
                'code_name', flat=True
            )
        except Exception:
            return False
        if request.method == 'GET' and 'view_audit_report' in user_permissions:
            return True
        return False


class AuditReportApiView(ListAPIView):
    permission_classes = [AuditReportPermission]
    queryset = Audit.objects.all().prefetch_related("audit_details")
    serializer_class = AuditReportSerializer


class ItemAuditViewSet(ModelViewSet):
    queryset = ItemAudit.objects.all().prefetch_related(
        Prefetch("item_audit_details", queryset=ItemAuditDetail.objects.all())
    )
    http_method_names = ['post', 'get']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaveItemAuditSerializer
        else:
            return GetItemAuditSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GetItemAuditSummarySerializer(instance)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            request.data['item_audit_details']
        except KeyError:
            return Response({"msg": "Please provide item_audit_details"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['audit_no'] = generate_item_audit_no()
        serializer = SaveItemAuditSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

