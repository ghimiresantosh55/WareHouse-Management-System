from django.shortcuts import render
from src.sale.sale_unique_id_generator import generate_sale_no
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
import django_filters
from .models import Repair, RepairDetail, RepairUser
from .serializers import RepairSerializer,  SaveRepairDetailSerializer, RepairDetailSerializer, RepairUserSerializer
from .repair_permissions import RepairPermission, RepairUserPermission
from django.db import transaction
from src.custom_lib.functions.current_user import get_created_by
from django.utils import timezone
from src.sale.direct_sale.serializers import SaveDirectSaleMasterSerializer


class FilterForRepair(django_filters.FilterSet):
    '''
    filter for repair
    '''
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
   
    class Meta:
        model = Repair
        fields = ['customer', 'expected_date_to_repair_ad','expected_date_to_repair_bs','repair_status']


class RepairViewSet(viewsets.ModelViewSet):
    '''
    model viewset for repair
    '''
    permission_classes = [RepairPermission]
    queryset = Repair.objects.all()
    serializer_class = RepairSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForRepair
    search_fields = [ 'customer__first_name','id']
    ordering_fields = ['id', ]
    http_method_names = ['get', 'head', 'post', 'patch']



    @transaction.atomic
    def partial_update(self, request, pk, *args, **kwargs):
        '''
        partial update  method
        '''
        date_now = timezone.now()
        current_user_id = get_created_by({"request":request}).id 
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST) 

        repair_instance = Repair.objects.get(id=pk)
        repair_details_update_data = list()
        repair_details_create_data = list()

        repair_details_data = request.data.pop('repair_details')
       
        for repair_detail_data in repair_details_data:
            if "id" in  repair_detail_data:
                repair_details_update_data.append(repair_detail_data)
            else: 
                repair_details_create_data.append(repair_detail_data)
        
        for  repair_detail_update_data in  repair_details_update_data:
                repair_details_instance = RepairDetail.objects.get(id = int(repair_detail_update_data['id']))
                # print(repair_details_instance)
                repair_details_update_serializer = RepairDetailSerializer(repair_details_instance, context={"request":request}, data= repair_detail_update_data, partial=True)
                if  repair_details_update_serializer.is_valid():
                    repair_details_update_serializer.save()
                    print( repair_details_update_serializer.data, "this is updated detail data")
                else: 
                    return Response(repair_details_update_serializer.errors, status= status.HTTP_400_BAD_REQUEST)


        for  repair_detail_create_data in  repair_details_create_data:
                repair_detail_create_data['repair'] = repair_instance.id
                repair_detail_create_data['created_by'] = current_user_id
                repair_detail_create_data['created_date_ad'] =  date_now
                
                repair_details_create_serializer = SaveRepairDetailSerializer(data=repair_detail_create_data, context={"request":request})
                if  repair_details_create_serializer.is_valid(raise_exception=True):
                       repair_details_create_serializer.save()
                else: 
                    return Response(repair_details_create_serializer.errors, status= status.HTTP_400_BAD_REQUEST)
     
           
        repair_serializer = RepairSerializer(repair_instance, data=request.data, partial=True, context={'request': request})
        if repair_serializer.is_valid(raise_exception=True):
              repair_serializer.save()
              return Response(repair_serializer.data, status= status.HTTP_200_OK)
        else:
            return Response(repair_serializer.errors, status= status.HTTP_400_BAD_REQUEST) 
   

class FilterForRepairUser(django_filters.FilterSet):
    '''
    filter for repair user
    '''
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
   
    class Meta:
        model = RepairUser
        fields = ['id', 'repair_status','repair_detail','comments']


class RepairUserViewSet(viewsets.ModelViewSet):
    '''
    model viewset for repair user
    '''
    permission_classes = [RepairUserPermission]
    queryset = RepairUser.objects.all()
    serializer_class=RepairUserSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForRepairUser
    search_fields = ['comments']
    ordering_fields = ['id', ]
    http_method_names = ['get', 'patch']

   
    def partial_update(self, request, *args, **kwargs):
        try:
            sale_master=request.data.pop('sale_master')
        except KeyError:
                return Response('Provide sale_master data in sale_master key',
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            repair_user=request.data.pop('repair_user')
        except KeyError:
                return Response('Provide repair user data in repair_user key',
                            status=status.HTTP_400_BAD_REQUEST)
                            
        sale_master["sale_no"] = generate_sale_no(1)
        sale_master["sale_type"] = 1
        sale_master['pay_type'] = 2
        
        sale_serializer = SaveDirectSaleMasterSerializer(
                    data= sale_master, context={"request": request})

        if sale_serializer.is_valid(raise_exception=True):
            sale_serializer.save()

        instance = self.get_object()
        repair_user_serializer=RepairUserSerializer(
                    instance, data= repair_user,partial= True, context={"request": request})
       
        if repair_user_serializer.is_valid(raise_exception=True):
            repair_user_serializer.save()
            return Response(repair_user_serializer.data, status=status.HTTP_200_OK)
        return Response(repair_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        