from decimal import Decimal

import django_filters
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery, Sum, DecimalField, Q, F
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.credit_management.models import CreditClearance
from src.customer_order.models import OrderMaster, OrderDetail
from src.financial_report.serializer.custom_serializer import BasicPartyPaymentSummaryReportSerializer
# from core_app.models import FiscalSessionAD
from src.party_payment.models import BasicPartyPayment, BasicPartyPaymentDetail, PartyPaymentDetail, PartyPayment
from src.purchase.models import PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge
from src.purchase.models import PurchaseOrderMaster, PurchaseOrderDetail
from src.purchase.serializers import PurchaseMasterSerializer
from src.sale.models import SaleMaster, SaleDetail, SalePaymentDetail
from src.supplier.models import Supplier
from src.user_group.models import CustomPermission
from .financial_report_permissions import (PurchaseOrderReportPermission, PurchaseReportPermission,
                                           BasicPartyPaymentDetailReportPermission,
                                           SaleReportPermission,
                                           CustomerOrderReportPermission, StockAdjustmentReportPermission,
                                           BasicPartyPaymentReportPermission, ChalanReportPermission,
                                           PartyPaymentReportPermission,
                                           PartyPaymentDetailReportPermission, CreditClearanceReportPermission,
                                           CustomerCreditReportPermission)
from .serializer.customer_credit_summary_serializers import SaleCreditReportSummarySerializer
from .serializer.purchase_order_serializers import (
    SummaryPurchaseOrderMasterSerializer, ReportPurchaseOrderMasterSerializer, )
from .serializers import (CustomerOrderSummarySerializer, CustomerOrderMasterReportSerializer,
                          CustomerOrderDetailReportSerializer, ReportBasicPartyPaymentDetailSerializer,
                          ReportChalanDetailSerializer,
                          ReportChalanSerializer, SummaryChalanMasterSerializer, ReportPartyPaymentSerializer,
                          ReportPartyPaymentDetailSerializer, SummaryPartyPaymentSerializer,
                          CreditClearanceReportSerializer,
                          ReportSupplierPartyPaymentSerializer)
from .serializers import (
    ItemwisePurchaseReportSerializer,
    GetFiscalSessionADSerializer, GetSupplierSerializer,
    GetFiscalSessionBSSerializer)
from .serializers import (ReportPurchaseMasterSerializer, ReportPurchaseDetailSerializer,
                          ReportPurchasePaymentDetailSerializer, ReportBasicPartyPaymentSerializer,
                          ReportPurchaseAdditionalChargeSerializer, SummaryPurchaseMasterSerializer)
from .serializers import (ReportSaleDetailSerializer, ReportSaleMasterSerializer, ReportSalePaymentDetailSerializer,
                          SummarySaleMasterSerializer, SaleCreditReportSerializer, StockAdjustmentSummarySerializer,
                          SummaryBasicPartyPaymentSerializer)
from ..chalan.models import ChalanMaster, ChalanDetail
from ..customer.models import Customer
from ..sale.serializers import UserSaleReportSerializer

"""_______________________________ views for purchase order__________________________________________________________"""

User = get_user_model()


class FilterForPurchaseOrderMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseOrderMaster
        fields = ['id', 'order_no', 'created_date_ad', 'supplier',
                  'created_by', 'order_type', 'ref_purchase_order']


class FilterForPurchaseOrderDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseOrderDetail
        fields = ['id', 'created_by', 'created_date_ad', 'item', 'item_category', 'purchase_order',
                  'taxable', 'discountable', 'ref_purchase_order_detail']


class PurchaseOrderMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderReportPermission]
    queryset = PurchaseOrderMaster.objects.all()
    serializer_class = ReportPurchaseOrderMasterSerializer
    filter_class = FilterForPurchaseOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id', 'order_no']


class PurchaseOrderSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderReportPermission]
    queryset = PurchaseOrderMaster.objects.all()
    serializer_class = SummaryPurchaseOrderMasterSerializer
    filter_class = FilterForPurchaseOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id']


"""_______________________________ views for purchase order__________________________________________________________"""


class FilterForPurchaseMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    # item = django_filters.NumberFilter(field_name="purchase_details__item")

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'created_by', 'created_date_ad', 'bill_date_ad', 'due_date_ad', 'purchase_type',
                  'supplier', 'purchase_details__item',
                  'discount_scheme', 'ref_purchase', 'ref_purchase_order']


class FilterForPurchaseDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'created_by', 'created_date_ad', 'item', 'item_category',
                  'taxable', 'discountable', 'ref_purchase_order_detail', 'ref_purchase_detail']


class PurchaseMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = ReportPurchaseMasterSerializer
    filter_class = FilterForPurchaseMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'purchase_type', 'chalan_no', 'remarks']
    ordering_fields = ['id']


class PurchaseDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseDetail.objects.all()
    serializer_class = ReportPurchaseDetailSerializer
    filter_class = FilterForPurchaseDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name', 'item_category__name']
    ordering_fields = ['id']


# itemwise purchase report
class ItemwisePurchaseReportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = PurchaseDetail.objects.all()
    serializer_class = ItemwisePurchaseReportSerializer
    filter_class = FilterForPurchaseDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name']
    ordering_fields = ['id']


class PurchasePaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchasePaymentDetail.objects.all()
    serializer_class = ReportPurchasePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'purchase_master', 'payment_mode']
    search_fields = ['id']
    ordering_fields = ['id']


class PurchaseAdditionalChargeReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseAdditionalCharge.objects.all()
    serializer_class = ReportPurchaseAdditionalChargeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'purchase_master', 'charge_type']
    search_fields = ['id']
    ordering_fields = ['id']


class PurchaseSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseReportPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = SummaryPurchaseMasterSerializer
    filter_class = FilterForPurchaseMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'supplier__name',
                     'created_by__user_name', 'discount_scheme__name', 'purchase_type', 'chalan_no', 'remarks']
    ordering_fields = ['id']


"""_______________________________ views for sale __________________________________________________________"""


class FilterForSaleMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'created_by', 'created_date_ad', 'sale_type', 'customer',
                  'discount_scheme', 'ref_sale_master']


class FilterForSaleDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleDetail
        fields = ['id', 'created_by', 'created_date_ad', 'item', 'item_category', 'sale_master',
                  'taxable', 'discountable', 'ref_sale_detail']


class SaleMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = ReportSaleMasterSerializer
    filter_class = FilterForSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no', 'customer__first_name',
                     'created_by__user_name', 'discount_scheme__name', 'sale_type', 'ref_by', 'remarks']
    ordering_fields = ['id']


class SaleDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SaleDetail.objects.all()
    serializer_class = ReportSaleDetailSerializer
    filter_class = FilterForSaleDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name', 'item_category__name']
    ordering_fields = ['id']


class SalePaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SalePaymentDetail.objects.all()
    serializer_class = ReportSalePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id', 'sale_master', 'payment_mode']
    search_fields = ['id']
    ordering_fields = ['id']


class SaleSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReportPermission]
    queryset = SaleMaster.objects.all()
    serializer_class = SummarySaleMasterSerializer
    filter_class = FilterForSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no', 'customer__first_name',
                     'created_by__user_name', 'discount_scheme__name', 'sale_type', 'ref_by', 'remarks']
    ordering_fields = ['id']


"""________________________ views for credit report __________________________________________"""


class FilterForCreditSaleMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'created_by', 'created_date_ad', 'sale_type', 'customer']


class SaleCreditReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditClearanceReportPermission]
    queryset = SaleMaster.objects.filter(pay_type=2)
    serializer_class = SaleCreditReportSerializer
    filter_class = FilterForCreditSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no']
    ordering_fields = ['sale_id', 'created_date_ad']


class SaleCreditReportSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CreditClearanceReportPermission]
    queryset = SaleMaster.objects.filter(pay_type=2)
    serializer_class = SaleCreditReportSummarySerializer
    filter_class = FilterForCreditSaleMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['sale_no']
    ordering_fields = ['sale_id', 'created_date_ad']


"""___________________________________ views for customer orders _____________________________________________"""


class FilterForCustomerOrderMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = OrderMaster
        fields = ['id', 'customer', 'discount_scheme', 'created_date_ad', 'status', 'created_by']


class FilterForCustomerOrderDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = OrderDetail
        fields = ['order', 'id', 'item', 'created_by']


class CustomerOrderSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderReportPermission]
    queryset = OrderMaster.objects.all()
    serializer_class = CustomerOrderSummarySerializer
    filter_class = FilterForCustomerOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no']
    ordering_fields = ['id', 'created_date_ad', 'status']


class CustomerOrderMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderReportPermission]
    serializer_class = CustomerOrderMasterReportSerializer
    filter_class = FilterForCustomerOrderMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no']
    ordering_fields = ['id', 'created_date_ad', 'status']

    def get_queryset(self):
        user = self.request.user
        groups = user.groups.filter(is_active=True).values_list('id', flat=True)
        user_permissions = CustomPermission.objects.filter(customgroup__in=groups)
        if user.is_superuser:
            return OrderMaster.objects.all()
        elif user_permissions.filter(code_name="view_customer_order_report").exists():
            return OrderMaster.objects.all()
        elif user_permissions.filter(code_name="self_view_customer_order_report").exists():
            return OrderMaster.objects.filter(created_by=user)


class CustomerOrderDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomerOrderReportPermission]
    queryset = OrderDetail.objects.all()
    serializer_class = CustomerOrderDetailReportSerializer
    filter_class = FilterForCustomerOrderDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['item']
    ordering_fields = ['id', 'created_date_ad', 'order']


class FilterForStockAdjustment(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'created_by', 'date', 'purchase_type', 'supplier']


class StockAdjustmentReportViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [PurchaseReportPermission]
    queryset = PurchaseMaster.objects.filter(Q(purchase_type=4) | Q(purchase_type=5))
    serializer_class = PurchaseMasterSerializer
    filter_class = FilterForStockAdjustment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'supplier__name',
                     'created_by__user_name', 'purchase_type']
    ordering_fields = ['id']


class StockAdjustmentSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [StockAdjustmentReportPermission]
    queryset = PurchaseMaster.objects.filter(Q(purchase_type=4) | Q(purchase_type=5))
    serializer_class = StockAdjustmentSummarySerializer
    filter_class = FilterForStockAdjustment


class FilterForBasicPartyPayment(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = BasicPartyPayment
        fields = ['id', 'supplier', 'created_by', 'created_date_ad', 'payment_type', 'amount',
                  'receipt_no', 'payment_date_ad', 'payment_date_bs', 'fiscal_session_ad', 'fiscal_session_bs']


class BasicPartyPaymentReportViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BasicPartyPaymentReportPermission]
    queryset = BasicPartyPayment.objects.all()
    serializer_class = ReportBasicPartyPaymentSerializer
    filter_class = FilterForBasicPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['supplier', 'supplier__name', 'amount', 'recipt_no',
                     'created_by__user_name', 'payment_date_ad', 'payment_date_bs', 'fiscal_session_ad',
                     'fiscal_session_bs', 'payment_type', 'remarks']
    ordering_fields = ['id', 'created_date_ad', 'fiscal_session_ad', 'fiscal_session_bs']


class BasicPartyPaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BasicPartyPaymentDetailReportPermission]
    queryset = BasicPartyPaymentDetail.objects.all()
    serializer_class = ReportBasicPartyPaymentDetailSerializer


class BasicPartyPaymentSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BasicPartyPaymentReportPermission]
    queryset = BasicPartyPayment.objects.all()
    serializer_class = SummaryBasicPartyPaymentSerializer
    filter_class = FilterForBasicPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['supplier__name',
                     'created_by__user_name', 'payment_type', 'receipt_no', 'payment_date_ad', 'payment_date_bs',
                     'fiscal_session_ad', 'fiscal_session_bs']
    ordering_fields = ['id']

    @action(url_path="get-data", detail=False)
    def get_data(self, request):
        # def list(self, request, **kwargs):
        data = {}
        fiscal_session_ad = FiscalSessionAD.objects.all()
        fiscal_session_ad_serializer = GetFiscalSessionADSerializer(fiscal_session_ad, many=True)
        fiscal_session_bs = FiscalSessionBS.objects.all()
        fiscal_session_bs_serializer = GetFiscalSessionBSSerializer(fiscal_session_bs, many=True)
        suppliers = Supplier.objects.filter(active=True)
        supplier_serializer = GetSupplierSerializer(suppliers, many=True)
        data['fiscal_session_ad'] = fiscal_session_ad_serializer.data
        data['fiscal_session_bs'] = fiscal_session_bs_serializer.data
        data['suppliers'] = supplier_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @action(url_path="summary", detail=False)
    def summary(self, request):
        if request.GET.get("id", None) is None:
            summary_queryset = BasicPartyPayment.objects.raw(f'''select id, first_name, middle_name, last_name, total_purchase_cash, 
                total_purchase_credit, total_purchase_return_cash,
                total_purchase_return_credit, party_payment_payment, party_payment_payment_return, 
                total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit to_be_paid,
                 total_purchase_cash + party_payment_payment - party_payment_payment_return paid_amount,
                (total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit) -
                (total_purchase_cash + party_payment_payment - party_payment_payment_return)
                 adv_due_amount
                from (select
                    id, first_name, middle_name, last_name, 
                    sum(total_purchase_cash) as total_purchase_cash,
                        sum(total_purchase_credit) as total_purchase_credit,
                        sum(total_purchase_return_cash) as total_purchase_return_cash,
                        sum(total_purchase_return_credit) as total_purchase_return_credit,
                        sum(party_payment_payment) as party_payment_payment,
                        sum(party_payment_payment_return) as party_payment_payment_return
                from
                    (
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        sum(grand_total) as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        sum(grand_total) as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        sum(grand_total) as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        sum(grand_total) as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        sum(amount) as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        sum(amount) as party_payment_payment_return
                    from
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ) R
                        group by id, first_name, middle_name, last_name
                        order by id) S''')

        else:
            supplier_filter = tuple()
            supplier_filter = request.GET.get("id", None)
            summary_queryset = BasicPartyPayment.objects.raw(f'''select id, first_name, middle_name, last_name, total_purchase_cash, 
                total_purchase_credit, total_purchase_return_cash,
                total_purchase_return_credit, party_payment_payment, party_payment_payment_return, 
                total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit to_be_paid,
                 total_purchase_cash + party_payment_payment - party_payment_payment_return paid_amount,
                (total_purchase_cash + total_purchase_credit - total_purchase_return_cash - total_purchase_return_credit) -
                (total_purchase_cash + party_payment_payment - party_payment_payment_return)
                 adv_due_amount
                from (select
                    id, first_name, middle_name, last_name, 
                    sum(total_purchase_cash) as total_purchase_cash,
                        sum(total_purchase_credit) as total_purchase_credit,
                        sum(total_purchase_return_cash) as total_purchase_return_cash,
                        sum(total_purchase_return_credit) as total_purchase_return_credit,
                        sum(party_payment_payment) as party_payment_payment,
                        sum(party_payment_payment_return) as party_payment_payment_return
                from
                    (
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        sum(grand_total) as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        sum(grand_total) as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 1
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        sum(grand_total) as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        sum(grand_total) as total_purchase_return_credit,
                        0 as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.purchase_purchasemaster pm
                    join chinari_dang.supplier_supplier sr on
                        pm.supplier_id = sr.id
                    where
                        purchase_type = 2
                        and pay_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        sum(amount) as party_payment_payment,
                        0 as party_payment_payment_return
                    from
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 1
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name
                union all
                    select
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ,
                        0 as total_purchase_cash,
                        0 as total_purchase_credit,
                        0 as total_purchase_return_cash,
                        0 as total_purchase_return_credit,
                        0 as party_payment_payment,
                        sum(amount) as party_payment_payment_return
                    from
                        chinari_dang.party_payment_basicpartypayment pp
                    join chinari_dang.supplier_supplier sr on
                        pp.supplier_id = sr.id
                    where
                        payment_type = 2
                    group by
                        sr.id,
                        sr.first_name ,
                        sr.middle_name ,
                        sr.last_name ) R
                        group by id, first_name, middle_name, last_name
                        order by id) S where id = {supplier_filter}; ''')

        basicSerializer = BasicPartyPaymentSummaryReportSerializer(summary_queryset, many=True)
        return Response(basicSerializer.data, status=status.HTTP_200_OK)


"""_______________________________ views for chalan__________________________________________________________"""


class FilterForChalanMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = ChalanMaster
        fields = ['id', 'chalan_no', 'created_by', 'created_date_ad', 'status',
                  'customer', 'chalan_details__item',
                  'discount_scheme', 'ref_order_master', 'ref_chalan_master']


class FilterForChalanDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = ChalanDetail
        fields = ['id', 'created_by', 'created_date_ad', 'item', 'item_category',
                  'taxable', 'discountable', 'ref_chalan_detail', 'ref_purchase_detail',
                  'ref_order_detail']


class ChalanMasterReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ChalanReportPermission]
    queryset = ChalanMaster.objects.all()
    serializer_class = ReportChalanSerializer
    filter_class = FilterForChalanMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['chalan_no', 'customer__first_name',
                     'created_by__user_name', 'discount_scheme__name', 'status', 'remarks']
    ordering_fields = ['id']


class ChalanDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ChalanReportPermission]
    queryset = ChalanDetail.objects.all()
    serializer_class = ReportChalanDetailSerializer
    filter_class = FilterForChalanDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name', 'item_category__name']
    ordering_fields = ['id']


class ChalanSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ChalanReportPermission]
    queryset = ChalanMaster.objects.all()
    serializer_class = SummaryChalanMasterSerializer
    filter_class = FilterForChalanMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['chalan_no', 'customer_first_name', 'ref_order_master__order_no'
                                                         'created_by__user_name', 'discount_scheme__name', 'status',
                     'remarks']
    ordering_fields = ['id']


class FilterForUserSaleReport(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    created_by = django_filters.NumberFilter(field_name="ref_order_detail__created_by", label="created_by")

    class Meta:
        model = SaleDetail
        fields = ['id', 'date', 'item', 'created_by']


def user_sale_helper():
    return SaleDetail.objects.filter(sale_master__sale_type=1) \
        .values('item', 'ref_order_detail__created_by').annotate(
        item_code=F('item__code'),
        item_name=F('item__name'),
        created_by_username=F('ref_order_detail__created_by__user_name'),
        created_by=F('ref_order_detail__created_by'),
        sale_qty=Sum('qty') - Coalesce(Sum('saledetail__qty', output_field=DecimalField()), Decimal("0.00")),
        sale_cost=Sum('net_amount') -
                  Coalesce(Sum('saledetail__net_amount', output_field=DecimalField()), Decimal("0.00")),
    )


class UserSaleReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderDetail.objects.values('item', 'created_by')
    permission_classes = [SaleReportPermission]
    serializer_class = UserSaleReportSerializer
    filter_class = FilterForUserSaleReport
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)

    def get_queryset(self):
        groups = self.request.user.groups.filter(is_active=True).values_list('id', flat=True)
        user_permissions = CustomPermission.objects.filter(customgroup__in=groups).values_list(
            'code_name', flat=True
        )
        if self.request.user.is_superuser or 'view_item_sale_report' in user_permissions:
            return user_sale_helper()
        if 'self_user_item_sale_report' in user_permissions:
            return user_sale_helper().filter(ref_order_detail__created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


"""_______________________________ views for party_payment __________________________________________________________"""


class FilterForPartyPayment(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="party_payments__created_date_ad")

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'purchase_type', 'supplier', 'supplier__name']


class FilterForSupplierPartyPayment(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="purchasemaster__party_payments__created_date_ad")

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'pan_vat_no', 'created_by', 'created_by__user_name', 'created_date_ad',
                  'created_date_bs']


class FilterForPartyPaymentDetail(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PartyPaymentDetail
        fields = ['id', 'created_by', 'created_date_ad', 'payment_mode__name', 'amount',
                  'party_payment']


class PartyPaymentReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentReportPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = ReportPartyPaymentSerializer
    filter_class = FilterForPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'id', 'supplier__name', 'purchase_type']
    ordering_fields = ['id', 'created_date_ad']


class SupplierPartyPaymentReportViewSet(ListAPIView):
    permission_classes = [PartyPaymentReportPermission]
    queryset = Supplier.objects.all()
    serializer_class = ReportSupplierPartyPaymentSerializer
    filter_class = FilterForSupplierPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'name']
    ordering_fields = ['id', 'created_date_ad']

    def get_queryset(self):
        total_amount = PurchaseMaster.objects.filter(
            supplier=OuterRef('pk'), pay_type=2, purchase_type=1).values('supplier').annotate(
            total_amount=Sum('grand_total')).values('total_amount')
        returned_amount = PurchaseMaster.objects.filter(
            supplier=OuterRef('pk'), purchase_type=2, pay_type=2).values('supplier').annotate(
            returned_amount=Sum('grand_total')).values('returned_amount')
        paid_amount = PartyPayment.objects.filter(
            purchase_master__supplier=OuterRef('pk'), payment_type=1).values('purchase_master__supplier').annotate(
            paid_amount=Sum('total_amount')).values('paid_amount')
        refund_amount = PartyPayment.objects.filter(
            purchase_master__supplier=OuterRef('pk'), payment_type=2).values('purchase_master__supplier').annotate(
            refund_amount=Sum('total_amount')).values('refund_amount')

        queryset = Supplier.objects.filter(active=True).annotate(
            created_by_user_name=F('created_by__user_name'),
            total_amount=Coalesce(
                Subquery(total_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            returned_amount=Coalesce(
                Subquery(returned_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            paid_amount=Coalesce(
                Subquery(paid_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            refund_amount=Coalesce(
                Subquery(refund_amount, output_field=DecimalField()), Decimal("0.00")
            )
        ).annotate(
            due_amount=(F('total_amount') - F('returned_amount')) - (F('paid_amount') - F('refund_amount'))
        ).filter(total_amount__gt=0).values(
            'id', 'name', 'pan_vat_no', 'paid_amount', 'refund_amount',
            'total_amount', 'returned_amount', 'due_amount', 'created_by_user_name'
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)


class PartyPaymentSummaryReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentReportPermission]
    queryset = PurchaseMaster.objects.all()
    serializer_class = SummaryPartyPaymentSerializer
    filter_class = FilterForPartyPayment
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'id', 'supplier__name', 'purchase_type']
    ordering_fields = ['id', 'created_date_ad']


class PartyPaymentDetailReportViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyPaymentDetailReportPermission]
    queryset = PartyPaymentDetail.objects.all()
    serializer_class = ReportPartyPaymentDetailSerializer
    filter_class = FilterForPartyPaymentDetail
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['party_payment', 'payment_mode__name', 'remarks', 'amount', 'created_by__user_name',
                     'party_payment__payment_type']
    ordering_fields = ['id', 'created_date_ad']


class FilterForCreditClearanceMaster(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'created_by', 'created_by__user_name', 'created_date_ad', 'created_date_bs']


class CreditClearanceReportViewSet(ListAPIView):
    permission_classes = [CustomerCreditReportPermission]
    queryset = Customer.objects.all()
    serializer_class = CreditClearanceReportSerializer
    filter_class = FilterForCreditClearanceMaster
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'first_name', 'last_name']
    ordering_fields = ['id', 'created_date_ad']

    def get_queryset(self):
        total_amount = SaleMaster.objects.filter(
            customer=OuterRef("pk"), pay_type=2, ref_sale_master__isnull=True).values('customer').annotate(
            total_amount=Sum('grand_total')).values('total_amount')
        returned_amount = SaleMaster.objects.filter(
            customer=OuterRef("pk"), sale_type=2, pay_type=2).values('customer').annotate(
            returned_amount=Sum('grand_total')).values('returned_amount')
        paid_amount = CreditClearance.objects.filter(
            sale_master__customer=OuterRef("pk"), payment_type=1).values('sale_master__customer').annotate(
            paid_amount=Sum('total_amount')).values('paid_amount')
        refund_amount = CreditClearance.objects.filter(
            sale_master__customer=OuterRef("pk"), payment_type=2).values('sale_master__customer').annotate(
            refund_amount=Sum('total_amount')).values('refund_amount')

        queryset = Customer.objects.filter(active=True).annotate(
            created_by_user_name=F('created_by__user_name'),
            total_amount=Coalesce(
                Subquery(total_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            returned_amount=Coalesce(
                Subquery(returned_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            paid_amount=Coalesce(
                Subquery(paid_amount, output_field=DecimalField()), Decimal("0.00")
            ),
            refund_amount=Coalesce(
                Subquery(refund_amount, output_field=DecimalField()), Decimal("0.00")
            )
        ).annotate(
            due_amount=(F('total_amount') - F('returned_amount')) - (F('paid_amount') - F('refund_amount'))
        ).filter(total_amount__gt=0).values(
            'id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no', 'total_amount',
            'returned_amount', 'paid_amount', 'refund_amount', 'due_amount',
            'created_by_user_name'
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(queryset, status=status.HTTP_200_OK)
