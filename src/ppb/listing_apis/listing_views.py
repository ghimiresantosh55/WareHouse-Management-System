from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from .listing_serializers import (PPBItemListSerializer, PPBItemCategoryListSerializer, PPBItemUnitListSerializer)
from ...item.models import Item, ItemCategory, Unit


class PPBItemListAPIView(ListAPIView):
    queryset = Item.objects.filter(active=True)
    serializer_class = PPBItemListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['id', 'code']
    search_fields = ['code']


class PPBItemCategoryListAPIView(ListAPIView):
    queryset = ItemCategory.objects.filter(active=True)
    serializer_class = PPBItemCategoryListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['id', 'code']
    search_fields = ['code']


class PPBItemUnitListAPIView(ListAPIView):
    queryset = Unit.objects.filter(active=True)
    serializer_class = PPBItemUnitListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['id', 'name']
    search_fields = ['name']
