# Django-rest-framework
from decimal import Decimal

# from requests library
import django_filters
import requests
from django.db import connection, transaction
from django.db.models import Prefetch
from django.utils import timezone
# filter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from src.core_app.models import OrganizationSetup
# import core files
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_bs
from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from src.sale.models import (IRDUploadLog, SaleAdditionalCharge, SaleDetail, SaleMaster, SalePaymentDetail,
                             SalePrintLog)
# import purchase_order_serializer
from src.sale.serializers import (SaleDetailForSaleReturnSerializer, SaleDetailSerializer,
                                  SaleMasterSerializer, SalePaymentDetailSerializer,
                                  SaveSaleMasterSerializer, SaleMasterReturnedSerializer)
from tenant.utils import tenant_schema_from_request
from .sale_permissions import SalePermission, SaleReturnPermission, SaleReturnDropPermission
from .sale_return_serializer import SaveSaleMasterReturnSerializer, SaleReturnDropSerializer
from .sale_unique_id_generator import generate_sale_no
from .serializers import (SaleAdditionalChargeSerializer, SalePrintLogSerializer)


class SaleMasterView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SalePermission]
    queryset = SaleMaster.objects.all().select_related("discount_scheme", "customer", "ref_order_master")
    serializer_class = SaleMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_fields = ["customer", "sale_type"]
    ordering_fields = ["id", "sale_no"]


class SaleMasterSaleFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
    item = django_filters.NumberFilter(field_name='sale_details__item', distinct=True)

    class Meta:
        model = SaleMaster
        fields = ['id', 'customer', 'sale_type', 'item', 'date']


class SaleMasterSaleView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SalePermission]
    queryset = SaleMaster.objects.filter(sale_type=1).select_related("discount_scheme", "customer", "ref_order_master")
    serializer_class = SaleMasterSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_class = SaleMasterSaleFilterSet
    search_fields = ["sale_no", "customer__first_name"]
    ordering_fields = ["id", "sale_no"]



class SaleMasterReturnFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name='created_date_ad')
    item = django_filters.NumberFilter(field_name='sale_details__item', distinct=True)

    class Meta:
        model = SaleMaster
        fields = ['id', 'customer', 'sale_type', 'item', 'date', 'return_dropped', 'ref_sale_master']


class SaleMasterReturnView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReturnPermission]
    queryset = SaleMaster.objects.filter(sale_type=2).select_related("discount_scheme", "customer", "ref_order_master")
    serializer_class = SaleMasterReturnedSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_class = SaleMasterReturnFilterSet
    ordering_fields = ["id", "sale_no"]


class SaleDetailView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SalePermission]
    queryset = SaleDetail.objects.all().select_related("sale_master", "item", "item_category")
    serializer_class = SaleDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["item", "sale_master__customer"]
    filter_fields = ["sale_master", "item", "item_category"]
    ordering_fields = ["id", "sale_master", "sale_master__sale_no"]


class SalePaymentDetailView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SalePermission]
    queryset = SalePaymentDetail.objects.all().select_related("sale_master", "payment_mode")
    serializer_class = SalePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_master__customer"]
    filter_fields = ["sale_master", "id", "payment_mode"]
    ordering_fields = ["id"]


class SaleAdditionalChargeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SalePermission]
    queryset = SaleAdditionalCharge.objects.all().select_related("charge_type", "sale_master")
    serializer_class = SaleAdditionalChargeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["remarks"]
    filter_fields = ["sale_master", "id", "charge_type"]
    ordering_fields = ["id", 'charge_type', 'sale_master', 'amount']


class SaleDetailForReturnViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReturnPermission]
    serializer_class = SaleDetailForSaleReturnSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["item", "customer", "item__code"]
    filter_fields = ["sale_master", "item", "item_category"]
    ordering_fields = ["id", "sale_master"]

    def get_queryset(self):
        queryset = SaleDetail.objects.filter(
            ref_sale_detail__isnull=True
        ).prefetch_related(Prefetch(
            'sale_packing_type_code',
            queryset=SalePackingTypeCode.objects.filter(
                sale_packing_type_detail_code__salepackingtypedetailcode__isnull=True

            ).distinct('id').prefetch_related(Prefetch(
                'sale_packing_type_detail_code',
                queryset=SalePackingTypeDetailCode.objects.filter(
                    salepackingtypedetailcode__isnull=True
                )
            )
            )
        )
        ).select_related("sale_master", "item",
                         "item_category")
        return queryset


class SaveSaleView(CreateAPIView):
    permission_classes = [SalePermission]
    queryset = SaleMaster.objects.all().select_related("discount_scheme", "customer", "ref_order_master")
    serializer_class = SaveSaleMasterSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if OrganizationSetup.objects.first() is None:
            return Response({'organization setup': 'Please insert Organization setup before making any sale'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data["sale_no"] = generate_sale_no(1)
        request.data["sale_type"] = 1

        serializer = SaveSaleMasterSerializer(
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


@property
def save_data_to_ird(sale_master_id, request):
    api_url = "http://103.1.92.174:9050/api/bill"
    with connection.cursor() as cursor:
        cursor.execute(f"set search_path to {tenant_schema_from_request(request)}")
        sale_master = SaleMaster.objects.get(id=sale_master_id)
        customer = sale_master.customer
        organization_setup = OrganizationSetup.objects.first()
        fiscal_year = str(get_fiscal_year_code_bs()).replace("/", ".")
        customer_name = str(f"{customer.first_name}").replace("  ", " ")
        data = {
            "username": "Test_CBMS",
            "password": "test@321",
            "seller_pan": str(organization_setup.pan_no),  # from organization setup
            "buyer_pan": str(customer.pan_vat_no),  # from customer
            "fiscal_year": fiscal_year,  # get_fiscal year function e.g 77.78
            "buyer_name": customer_name,  # from customer first name, middle name, last name
            "invoice_number": sale_master.sale_no,  # Sale no
            "invoice_date": sale_master.created_date_bs,  # created_data_bs of sale
            "total_sale": float(sale_master.sub_total),  # Sub Total of sale
            "taxable_sale_vat": float(sale_master.total_tax),  # Tax amount of sale
            "vat": "0",  # vat of sale
            "excisable_amount": 0,  # zero 0
            "excise": 0,  # zero 0
            "taxable_sale_hst": 0,  # zero 0
            "hst": 0,  # zero 0
            "amount_for_esf": 0,  # zero 0
            "esf": 0,  # zero 0
            "export_sales": 0,  # zero 0
            "tax_exempted_sale": 0,  # zero 0
            "isrealtime": True,
            "datetimeClient": str(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))  # date('Y-m-d h:i:s');

        }
        try:
            response = requests.post(api_url, data=data)

        except:
            ird_update = IRDUploadLog.objects.create(sale_master=sale_master, status_code=504,
                                                     response_message="server time out",
                                                     created_by=sale_master.created_by,
                                                     created_date_bs=sale_master.created_date_ad)
            ird_update.save()
            print("server not Found")
        else:
            if response.status_code == "200":
                ird_update = IRDUploadLog.objects.create(sale_master=sale_master, status_code=response.status_code,
                                                         response_message="Log saved to IRD",
                                                         created_by=sale_master.created_by,
                                                         created_date_bs=sale_master.created_date_ad)
                ird_update.save()
                sale_master.is_real_time_upload = True
                sale_master.synced_with_ird = True
                sale_master.save()
            else:
                ird_update = IRDUploadLog.objects.create(sale_master=sale_master, status_code=response.status_code,
                                                         response_message="Log Not saved to IRD",
                                                         created_by=sale_master.created_by,
                                                         created_date_bs=sale_master.created_date_ad)
                ird_update.save()


class ReturnSaleView(CreateAPIView):
    permission_classes = [SaleReturnPermission]
    queryset = SaleMaster.objects.all().select_related("discount_scheme", "customer")
    serializer_class = SaveSaleMasterReturnSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        try:
            sale_details = request.data["sale_details"]
        except KeyError:
            return Response({"key_error": "Provide sale_details"}, status=status.HTTP_400_BAD_REQUEST)
        for sale in sale_details:
            ref_id_sale = int(sale["ref_sale_detail"])
            total_quantity = SaleDetail.objects.values_list(
                "qty", flat=True).get(pk=ref_id_sale)
            return_quantity = sum(SaleDetail.objects.filter(ref_sale_detail=ref_id_sale)
                                  .values_list("qty", flat=True)) + Decimal(sale["qty"])

            if total_quantity < return_quantity:
                return Response("Return items ({}) more than sale items({})".format(return_quantity, total_quantity),
                                status=status.HTTP_400_BAD_REQUEST)

        request.data["sale_no"] = generate_sale_no(2)
        request.data["sale_type"] = 2
        serializer = SaveSaleMasterReturnSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalePrintLogViewset(viewsets.ModelViewSet):
    permission_classes = [SalePermission]
    queryset = SalePrintLog.objects.all().select_related("sale_master")
    serializer_class = SalePrintLogSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_master"]
    filter_fields = ["id"]
    ordering_fields = ["id"]


class SaleReturnDropView(CreateAPIView):
    permission_classes = [SaleReturnDropPermission]
    serializer_class = SaleReturnDropSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(SaleReturnDropView, self).create(request, *args, **kwargs)


class SaleDetailReturnInfoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReturnPermission]

    serializer_class = SaleDetailForSaleReturnSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["item", "customer", "item__code"]
    filter_fields = ["sale_master", "item", "item_category"]
    ordering_fields = ["id", "sale_master"]

    def get_queryset(self):
        queryset = SaleDetail.objects.filter(
            sale_master__sale_type=2
        ).prefetch_related(Prefetch(
            'sale_packing_type_code',
            queryset=SalePackingTypeCode.objects.prefetch_related(
                'sale_packing_type_detail_code'
            )
        )
        ).select_related("sale_master", "item",
                         "item_category")
        return queryset
