from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from src.core_app.core_app_permissions import SystemSetupPermission
from .models import PurchaseDocument
from .models import PurchaseDocumentType
from .purchase_document_serializer import PurchaseDocumentSerializer, PurchaseDocumentTypeSerializer


class PurchaseDocumentViewSet(ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = PurchaseDocument.objects.all()
    serializer_class = PurchaseDocumentSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["id", "title"]
    ordering_fields = ['id']
    filter_fields = ['id', 'title']
    http_method_names = ['get', 'head', 'post', 'patch']


class PurchaseDocumentTypeViewSet(ModelViewSet):
    permission_classes = [SystemSetupPermission]
    queryset = PurchaseDocumentType.objects.all()
    serializer_class = PurchaseDocumentTypeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["id", "name"]
    ordering_fields = ['id']
    filter_fields = ['id', 'name']
    http_method_names = ['get', 'head', 'post', 'patch']
