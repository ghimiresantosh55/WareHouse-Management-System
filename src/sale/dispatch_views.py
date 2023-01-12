from django.db.models import Prefetch
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from .dispatch_serializer import DispatchSerializer, GetSaleForDispatchSerializer
from .models import SaleDetail, SaleMaster


class CreateDispatchViewSet(CreateAPIView):
    serializer_class = DispatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ListDispatchSaleView(ListAPIView):
    queryset = SaleMaster.objects.all()
    serializer_class = GetSaleForDispatchSerializer


    def get_queryset(self):
        queryset = super().get_queryset()
      
        queryset = queryset.filter(sale_details__dispatched=False).prefetch_related(
                Prefetch(
                    "sale_details",
                    queryset=SaleDetail.objects.filter(dispatched=False),
                  
                ),
            )
       
        return queryset
