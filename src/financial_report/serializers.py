# rest_framework
from decimal import Decimal

from rest_framework import serializers

from src.chalan.models import ChalanMaster, ChalanDetail
from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.credit_management.models import CreditClearance
from src.customer_order.models import OrderMaster, OrderDetail
from src.party_payment.models import BasicPartyPayment, BasicPartyPaymentDetail, PartyPayment, PartyPaymentDetail
from src.purchase.models import PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge
# Models from purchase app
from src.sale.models import SaleMaster, SaleDetail, SalePaymentDetail
from src.supplier.models import Supplier
from ..customer.models import Customer

"""-------------------------purchase_order_serializer for purchase  -----------------------------------------------------------"""


class ItemwisePurchaseReportSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='purchase.supplier.name', allow_null=True)
    purchase_no = serializers.ReadOnlyField(source='purchase.purchase_no', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'item_category']


class ReportPurchaseMasterSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    ref_purchase_no = serializers.ReadOnlyField(source='ref_purchase.purchase_no', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'supplier_name', 'created_by_user_name', 'discount_scheme_name', 'ref_purchase_order_no',
                     'ref_purchase'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportPurchaseDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order_detail', 'item_name', 'item_category_name',
                     'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportPurchasePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = PurchasePaymentDetail
        fields = "__all__"


class ReportPurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    charge_type_name = serializers.ReadOnlyField(source='charge_type.name', allow_null=True)

    class Meta:
        model = PurchaseAdditionalCharge
        fields = "__all__"


# purchase_order_serializer for Summary report of Purchase
class DetailPurchasePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = PurchasePaymentDetail
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DetailPurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseAdditionalCharge
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DetailPurchaseDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['purchase']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'expiry_date_ad', 'ref_purchase_order_detail', 'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# purchase master purchase_order_serializer for read_only views
class SummaryPurchaseMasterSerializer(serializers.ModelSerializer):
    purchase_details = DetailPurchaseDetailSerializer(many=True)
    payment_details = DetailPurchasePaymentDetailSerializer(many=True)
    additional_charges = DetailPurchaseAdditionalChargeSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    ref_purchase = serializers.ReadOnlyField(source='ref_purchase.purchase_no', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['purchase_type_display', 'pay_type_display', 'created_by', 'created_date_ad',
                            'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'discount_scheme', 'bill_no', 'due_date_ad', 'ref_purchase', 'ref_purchase_order',
                     'additional_charges'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class StockAdjustmentSummarySerializer(serializers.ModelSerializer):
    purchase_details = DetailPurchaseDetailSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['purchase_type_display', 'pay_type_display', 'created_by', 'created_date_ad',
                            'created_date_bs']


"""-------------------------purchase_order_serializer for Sale  -----------------------------------------------------------"""


class ReportSaleMasterSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_sale_master = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    sale_type_display = serializers.ReadOnlyField(source='get_sale_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = SaleMaster
        fields = "__all__"
        read_only_fields = ['sale_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'created_by_user_name', 'discount_scheme_name', 'ref_sale_master'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportSaleDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = SaleDetail
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'ref_sale_detail', 'item_name', 'item_category_name',
                     'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportSalePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = SalePaymentDetail
        fields = "__all__"


# purchase_order_serializer for summary report of sale
class DetailSalePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = SalePaymentDetail
        exclude = ['sale_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DetailSaleDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = SaleDetail
        exclude = ['sale_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'expiry_date_ad', 'ref_purchase_order_detail', 'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class SummarySaleMasterSerializer(serializers.ModelSerializer):
    sale_details = DetailSaleDetailSerializer(many=True)
    payment_details = DetailSalePaymentDetailSerializer(many=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_sale_master = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    sale_type_display = serializers.ReadOnlyField(source='get_sale_type_display', allow_null=True)

    class Meta:
        model = SaleMaster
        fields = "__all__"
        read_only_fields = ['sale_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'created_by_user_name', 'discount_scheme_name', 'ref_sale_master'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


"""_______________________ purchase_order_serializer for Credit Sale Report _______________________________________________"""


class SaleCreditReportSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    paid_amount = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    returned_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = SaleMaster
        fields = ['id', 'sale_no', 'customer', 'customer_first_name', 'customer_middle_name', 'customer_last_name',
                  'paid_amount', 'refund_amount', 'returned_amount', 'total_amount', 'created_date_ad',
                  'created_date_bs',
                  'created_by', 'created_by_user_name', 'remarks']

    def to_representation(self, instance):
        data = super(SaleCreditReportSerializer, self).to_representation(instance)

        # get due amount
        data['due_amount'] = (data['total_amount'] - data['returned_amount']) - (
                data['paid_amount'] - data['refund_amount'])
        return data

    def get_paid_amount(self, instance):
        # calculation of total_paid_amount with same fk
        paid_amount = sum(CreditClearance.objects.filter(sale_master=instance.id, payment_type=1)
                          .values_list('total_amount', flat=True))

        return paid_amount

    def get_refund_amount(self, instance):
        refund_amount = sum(CreditClearance.objects.filter(sale_master=instance.id, payment_type=2)
                            .values_list('total_amount', flat=True))
        return refund_amount

    def get_total_amount(self, instance):
        total_sale_amount = instance.grand_total
        return total_sale_amount

    def get_returned_amount(self, instance):
        sale_return_amount = sum(SaleMaster.objects.filter(ref_sale_master=instance.id)
                                 .values_list('grand_total', flat=True))
        return sale_return_amount


"""_________________________________serializers for customer order Report___________________________________________"""

from django.db.models import Sum


class CustomerOrderMasterReportSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    net_sale_amount = serializers.SerializerMethodField()

    class Meta:
        model = OrderMaster
        fields = "__all__"
        read_only_fields = ['status_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def get_net_sale_amount(self, instance):

        try:
            net_sale_amount = SaleMaster.objects.get(
                sale_type=1, ref_order_master=instance
            ).grand_total
            try:
                return_amount = SaleMaster.objects.filter(sale_type=2, ref_order_master=instance).values(
                    "ref_order_master"
                ).annotate(
                    return_amount=Sum("grand_total")
                ).values("return_amount")[0]['return_amount']
            except IndexError:
                return_amount = Decimal("0.00")
            return net_sale_amount - return_amount
        except SaleMaster.DoesNotExist:
            return Decimal("0.00")


class CustomerOrderDetailReportSerializer(serializers.ModelSerializer):
    order_no = serializers.ReadOnlyField(source='order.order_no', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)

    class Meta:
        model = OrderDetail
        fields = "__all__"


class CustomerOrderDetailSummaryReportSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)

    class Meta:
        model = OrderDetail
        exclude = ['order']


class CustomerOrderSummarySerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_details = CustomerOrderDetailSummaryReportSerializer(many=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = "__all__"
        read_only_fields = ['status_display', 'created_by', 'created_date_ad', 'created_date_bs']


class ReportBasicPartyPaymentSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    fiscal_session_ad_full = serializers.ReadOnlyField(source='fiscal_session_ad.session_full', allow_null=True)
    fiscal_session_bs_full = serializers.ReadOnlyField(source='fiscal_session_bs.session_full', allow_null=True)
    fiscal_session_ad_short = serializers.ReadOnlyField(source='fiscal_session_ad.session_short', allow_null=True)
    fiscal_session_bs_short = serializers.ReadOnlyField(source='fiscal_session_bs.session_short', allow_null=True)

    class Meta:
        model = BasicPartyPayment
        fields = "__all__"
        read_only_fields = ['payment_type_display', 'created_by', 'created_date_ad', 'created_date_bs']


class ReportBasicPartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    basic_party_payment_supplier_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.name',
                                                                  allow_null=True)

    class Meta:
        model = BasicPartyPaymentDetail
        fields = "__all__"


class DetailBasicPartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = BasicPartyPaymentDetail
        exclude = ['basic_party_payment']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class SummaryBasicPartyPaymentSerializer(serializers.ModelSerializer):
    basic_party_payment_details = DetailBasicPartyPaymentDetailSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name', allow_null=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    fiscal_session_ad_full = serializers.ReadOnlyField(source='fiscal_session_ad.session_full', allow_null=True)
    fiscal_session_bs_full = serializers.ReadOnlyField(source='fiscal_session_bs.session_full', allow_null=True)
    fiscal_session_ad_short = serializers.ReadOnlyField(source='fiscal_session_ad.session_short', allow_null=True)
    fiscal_session_bs_short = serializers.ReadOnlyField(source='fiscal_session_bs.session_short', allow_null=True)

    class Meta:
        model = BasicPartyPayment
        fields = "__all__"
        read_only_fields = ['payment_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'supplier_name', 'created_by_user_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class GetSupplierSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='country.name', allow_null=True)

    class Meta:
        model = Supplier
        exclude = ['created_date_ad', 'created_date_bs', 'created_by', 'active', 'image', 'country']


class GetFiscalSessionADSerializer(serializers.ModelSerializer):
    # country_name =serializer.ReadOnlyField(source='country.name', allow_null=True)
    class Meta:
        model = FiscalSessionAD
        exclude = ['created_date_ad', 'created_date_bs', 'created_by']


class GetFiscalSessionBSSerializer(serializers.ModelSerializer):
    # country_name =serializer.ReadOnlyField(source='country.name', allow_null=True)
    class Meta:
        model = FiscalSessionBS
        exclude = ['created_date_ad', 'created_date_bs', 'created_by']


# chalan serializer
class ReportChalanSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_no = serializers.ReadOnlyField(source='ref_order_master.order_no', allow_null=True)

    class Meta:
        model = ChalanMaster
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'customer_first_name', 'customer_last_name', 'created_by_user_name', 'discount_scheme_name',
                     'order_no'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportChalanDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = ChalanDetail
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'ref_chalan_detail', 'item_name', 'item_category_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class DetailChalanDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = ChalanDetail
        exclude = ['chalan_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'ref_chalan_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class SummaryChalanMasterSerializer(serializers.ModelSerializer):
    chalan_details = DetailChalanDetailSerializer(many=True, read_only=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_no = serializers.ReadOnlyField(source='ref_order_master.order_no', allow_null=True)

    class Meta:
        model = ChalanMaster
        fields = "__all__"


class ReportPartyPaymentSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    paid_amount = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    returned_amount = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'supplier_name',
                  'paid_amount', 'refund_amount', 'total_amount', 'returned_amount',
                  'created_by_user_name']

    def to_representation(self, instance):
        data = super(ReportPartyPaymentSerializer, self).to_representation(instance)
        data['due_amount'] = (data['total_amount'] - data['returned_amount']) - (
                data['paid_amount'] - data['refund_amount'])
        return data

    def get_paid_amount(self, instance):
        paid_amount = sum(PartyPayment.objects.filter(purchase_master=instance, payment_type=1)
                          .values_list('total_amount', flat=True))
        return paid_amount

    def get_refund_amount(self, instance):
        refund_amount = sum(PartyPayment.objects.filter(purchase_master=instance, payment_type=2)
                            .values_list('total_amount', flat=True))
        return refund_amount

    def get_total_amount(self, instance):
        total_amount = instance.grand_total
        return total_amount

    def get_returned_amount(self, instance):
        purchase_return_amount = sum(
            PurchaseMaster.objects.filter(ref_purchase=instance.id, purchase_type=2, pay_type=2)
                .values_list('grand_total', flat=True))
        return purchase_return_amount


class ReportPartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    party_payment_purchase_no = serializers.ReadOnlyField(source='party_payment.purchase_master.purchase_no',
                                                          allow_null=True)

    class Meta:
        model = PartyPaymentDetail
        fields = "__all__"


class DetailPartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PartyPaymentDetail
        exclude = ['party_payment']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class PartyPaymentReceiptForSummarySerializer(serializers.ModelSerializer):
    payment_type_name = serializers.ReadOnlyField(source='get_payment_type_display')

    class Meta:
        model = PartyPayment
        fields = ['id', 'payment_type', 'payment_type_name', 'receipt_no', 'total_amount']
        read_only_fields = fields


class SummaryPartyPaymentSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    paid_amount = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    returned_amount = serializers.SerializerMethodField()
    party_payments = PartyPaymentReceiptForSummarySerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'supplier_name',
                  'paid_amount', 'refund_amount', 'total_amount', 'returned_amount',
                  'created_by_user_name', 'party_payments']

    def to_representation(self, instance):
        data = super(SummaryPartyPaymentSerializer, self).to_representation(instance)
        data['due_amount'] = (data['total_amount'] - data['returned_amount']) - (
                data['paid_amount'] - data['refund_amount'])
        return data

    def get_paid_amount(self, instance):
        paid_amount = sum(PartyPayment.objects.filter(purchase_master=instance, payment_type=1)
                          .values_list('total_amount', flat=True))
        return paid_amount

    def get_refund_amount(self, instance):
        refund_amount = sum(PartyPayment.objects.filter(purchase_master=instance, payment_type=2)
                            .values_list('total_amount', flat=True))
        return refund_amount

    def get_total_amount(self, instance):
        total_amount = instance.grand_total
        return total_amount

    def get_returned_amount(self, instance):
        purchase_return_amount = sum(
            PurchaseMaster.objects.filter(ref_purchase=instance.id, purchase_type=2, pay_type=2)
                .values_list('grand_total', flat=True))
        return purchase_return_amount


"""_______________________ serializer for Credit Clearance Report _______________________________________________"""


class CreditClearanceReportSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    paid_amount = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    returned_amount = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'pan_vat_no',
                  'paid_amount', 'refund_amount', 'total_amount', 'returned_amount',
                  'created_by_user_name']

    def to_representation(self, instance):
        data = super(CreditClearanceReportSerializer, self).to_representation(instance)
        data['due_amount'] = (data['total_amount'] - data['returned_amount']) - (
                data['paid_amount'] - data['refund_amount'])
        return data

    def get_paid_amount(self, instance):
        # calculation of total_paid_amount with same fk
        paid_amount = sum(CreditClearance.objects.filter(
            sale_master__customer=instance, payment_type=1).distinct("id")
                          .values_list('total_amount', flat=True))

        return paid_amount

    def get_refund_amount(self, instance):
        refund_amount = sum(
            CreditClearance.objects.filter(sale_master__customer=instance, payment_type=2).distinct("id")
                .values_list('total_amount', flat=True))
        return refund_amount

    def get_total_amount(self, instance):
        total_sale_amount = sum(
            SaleMaster.objects.filter(
                customer=instance, pay_type=2, ref_sale_master__isnull=True).values_list(
                "grand_total", flat=True)
        )
        return total_sale_amount

    def get_returned_amount(self, instance):
        sale_return_amount = sum(SaleMaster.objects.filter(sale_type=2, pay_type=2, customer=instance)
                                 .values_list('grand_total', flat=True))
        return sale_return_amount


class ReportSupplierPartyPaymentSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    paid_amount = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    returned_amount = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'pan_vat_no',
                  'paid_amount', 'refund_amount', 'total_amount', 'returned_amount',
                  'created_by_user_name']

    def to_representation(self, instance):
        data = super(ReportSupplierPartyPaymentSerializer, self).to_representation(instance)
        data['due_amount'] = (data['total_amount'] - data['returned_amount']) - (
                data['paid_amount'] - data['refund_amount'])
        return data

    def get_paid_amount(self, instance):
        paid_amount = sum(PartyPayment.objects.filter(purchase_master__supplier=instance, payment_type=1).distinct("id")
                          .values_list('total_amount', flat=True))

        return paid_amount

    def get_refund_amount(self, instance):
        refund_amount = sum(
            PartyPayment.objects.filter(purchase_master__supplier=instance, payment_type=2).distinct("id")
                .values_list('total_amount', flat=True))
        return refund_amount

    def get_total_amount(self, instance):
        total_sale_amount = sum(
            PurchaseMaster.objects.filter(supplier=instance, pay_type=2, purchase_type=1).values_list("grand_total",
                                                                                                      flat=True)
        )
        return total_sale_amount

    def get_returned_amount(self, instance):
        sale_return_amount = sum(PurchaseMaster.objects.filter(purchase_type=2, pay_type=2, supplier=instance)
                                 .values_list('grand_total', flat=True))
        return sale_return_amount
