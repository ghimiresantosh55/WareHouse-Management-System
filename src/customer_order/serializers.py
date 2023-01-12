import decimal
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import DiscountScheme
from src.custom_lib.functions import current_user
from src.customer.models import Customer
from src.item.models import Item
from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from .models import OrderDetail, OrderMaster
from .order_unique_id_generator import generate_customer_order_no

# Used for Cancel order
from ..credit_management.models import CreditClearance
from ..sale.models import SaleMaster


class OrderMasterSerializer(serializers.ModelSerializer):
    # advanced_deposits = AdvancedDepositSerializer(many=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    is_picked = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    verified_by = serializers.ReadOnlyField(source='verified_by.user_name', read_only=True)
    approved_by_name = serializers.ReadOnlyField(source='approved_by.user_name', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = ['id', 'order_no', 'customer', 'customer_first_name', 'customer_last_name', 'pick_verified',
                  'created_by_user_name', 'status_display', 'customer', 'total_discount', 'status',
                  'total_tax', 'sub_total', 'delivery_date_ad', 'delivery_date_bs',
                  'delivery_location', 'grand_total', 'is_picked', 'remarks', 'created_date_ad',
                  'created_date_bs', 'by_batch', 'verified_by', 'approved', 'approved_by', 'approved_by_name',
                  'credit_term']
        read_only_fields = fields

    @staticmethod
    def get_is_picked(order_master):
        return not order_master.order_details.filter(cancelled=False, picked=False).exists()

    def get_customer(self, instance):
        return {
            "first_name": instance.customer.first_name,
            "last_name": instance.customer.last_name,
            "id": instance.customer.pk,
        }


# Read only serializer
class PackingTypeDetailCodePOViewSerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source='packing_type_detail_code.code')

    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code', 'code']
        read_only_fields = fields


class PackingTypeCodePOViewSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = PackingTypeDetailCodePOViewSerializer(many=True)
    code = serializers.ReadOnlyField(source='packing_type_code.code', allow_null=True)
    location_code = serializers.ReadOnlyField(source='packing_type_code.location.code', allow_null=True)
    location = serializers.ReadOnlyField(source='packing_type_code.location.id', allow_null=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'location_code', 'location', 'code', 'qty',
                  'sale_detail', 'packing_type_code', 'sale_packing_type_detail_code']
        read_only_fields = fields


class OrderDetailViewSerializer(serializers.ModelSerializer):
    customer_packing_types = PackingTypeCodePOViewSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(
        source='created_by.user_name', allow_null=True
    )
    order_by_batch = serializers.ReadOnlyField(source='order.by_batch', allow_null=True)
    picked_by_name = serializers.ReadOnlyField(source='picked_by.user_name', allow_null=True)

    class Meta:
        model = OrderDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


class OrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(
        source='created_by.user_name', allow_null=True
    )

    class Meta:
        model = OrderDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


class OrderSummaryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'code']


class OrderSummaryDetailSerializer(serializers.ModelSerializer):
    customer_packing_types = PackingTypeCodePOViewSerializer(many=True)
    item = OrderSummaryItemSerializer(read_only=True)
    batch_no = serializers.ReadOnlyField(source='purchase_detail.batch_no')

    class Meta:
        model = OrderDetail
        exclude = ['order']


class OrderSummaryCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'middle_name', 'last_name']


class OrderSummaryDiscountScheme(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = ['id', 'name', 'rate']


class OrderSummaryMasterSerializer(serializers.ModelSerializer):
    customer = OrderSummaryCustomerSerializer(read_only=True)
    discount_scheme = OrderSummaryDiscountScheme(read_only=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_details = OrderSummaryDetailSerializer(many=True, read_only=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    approved_by_name = serializers.ReadOnlyField(source='approved_by.user_name', read_only=True)

    # customer_order_additional_charges = CustomerOrderAdditionalChargeSerializer(many=True)

    class Meta:
        model = OrderMaster
        fields = ['id', 'order_details', 'order_no',
                  'created_by_user_name', 'status_display', 'customer', 'total_discount',
                  'discount_scheme', 'status',
                  'total_tax', 'sub_total', 'delivery_date_ad', 'delivery_date_bs',
                  'delivery_location', 'grand_total', 'remarks', 'created_date_ad', 'created_date_bs', 'by_batch',
                  'approved', 'approved_by', 'approved_by_name', 'credit_term']


# save customer order serializer

class SaveCustomerOrderPackTypeDetails(serializers.ModelSerializer):
    class Meta:
        model = SalePackingTypeDetailCode
        exclude = ['sale_packing_type_code']


class SaveCustomerOrderPackTypes(serializers.ModelSerializer):
    sale_packing_type_detail_code = SaveCustomerOrderPackTypeDetails(many=True)

    class Meta:
        model = SalePackingTypeCode
        exclude = ['customer_order_detail']


class SaveOrderDetailSerializer(serializers.ModelSerializer):
    customer_packing_types = SaveCustomerOrderPackTypes(many=True)

    class Meta:
        model = OrderDetail
        exclude = ['order', 'device_type', 'app_type']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveOrderSerializer(serializers.ModelSerializer):
    order_details = SaveOrderDetailSerializer(many=True)

    class Meta:
        model = OrderMaster
        fields = ['id', 'order_details', 'order_no', 'status', 'customer',
                  'discount_scheme', 'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'delivery_date_ad', 'delivery_date_bs', 'delivery_location', 'grand_total', 'remarks',
                  'credit_term'
                  ]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'order_no', 'status']

    def create(self, validated_data):
        self.create_validate(validated_data)
        date_now = timezone.now()

        order_details = validated_data.pop('order_details')
        created_by = current_user.get_created_by(self.context)
        order_master = OrderMaster.objects.create(
            order_no=generate_customer_order_no(),
            status=1,
            **validated_data, created_date_ad=date_now,
            created_by=created_by
        )

        # all the order are stored in OrderDetail
        for detail in order_details:
            customer_packing_types = detail.pop('customer_packing_types')
            order_detail_db = OrderDetail.objects.create(**detail, order=order_master,
                                                         created_by=created_by,
                                                         created_date_ad=date_now)
            for customer_pack_type in customer_packing_types:
                sale_pack_type_details = customer_pack_type.pop('sale_packing_type_detail_code')
                sale_pack_type_db = SalePackingTypeCode.objects.create(
                    **customer_pack_type,
                    customer_order_detail=order_detail_db
                )
                for sale_pack_type_detail in sale_pack_type_details:
                    SalePackingTypeDetailCode.objects.create(
                        **sale_pack_type_detail,
                        sale_packing_type_code=sale_pack_type_db
                    )

        return order_master

    def create_validate(self, data):
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        quantize_places = Decimal(10) ** -2
        # initialize variables to check
        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        customer_order_details = data['order_details']

        for customer_order in customer_order_details:
            customer_order_detail = {}
            key_values = zip(customer_order.keys(), customer_order.values())
            for key, values in key_values:
                customer_order_detail[key] = values

            # validation for amount values less than or equal to 0 "Zero"
            if customer_order_detail['tax_rate'] < 0 or customer_order_detail['discount_rate'] < 0 or \
                    customer_order_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {customer_order_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                                  ' cannot be less than 0'})

            if customer_order_detail['qty'] <= 0 or customer_order_detail['sale_cost'] <= 0:
                raise serializers.ValidationError({
                    f'item {customer_order_detail["item"].name}': 'values in fields, quantity, sale_cost cannot be less than'
                                                                  ' or equals to 0'})
            if customer_order_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {customer_order_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = customer_order_detail['sale_cost'] * customer_order_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != customer_order_detail['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {customer_order_detail["item"].name}': ' gross_amount calculation not valid : should be {}'.format(
                            gross_amount)})
            sub_total += gross_amount
            # validation for discount amount
            if customer_order_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + customer_order_detail['gross_amount']
                discount_rate = (customer_order_detail['discount_amount'] *
                                 Decimal('100')) / (customer_order_detail['sale_cost'] *
                                                    customer_order_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != customer_order_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {customer_order_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + customer_order_detail['discount_amount']
            elif customer_order_detail['discountable'] is False and customer_order_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                       f'discount_amount {customer_order_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - customer_order_detail['discount_amount']
            if customer_order_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = customer_order_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != customer_order_detail['tax_amount']:
                    raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                           f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif customer_order_detail['taxable'] is False:
                if customer_order_detail['tax_rate'] != 0 or customer_order_detail['tax_amount'] != 0:
                    raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                           "taxable = False, tax_rate and tax_amount should be 0"})
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((customer_order_detail['sale_cost'] *
                                           customer_order_detail['qty'] *
                                           customer_order_detail['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (customer_order_detail['sale_cost'] *
                                           customer_order_detail['qty'] *
                                           customer_order_detail['discount_rate']) / Decimal('100')) *
                          customer_order_detail['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != customer_order_detail['net_amount']:
                raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                       f'net_amount calculation not valid : should be {net_amount}'})
            grand_total = grand_total + net_amount

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                f'total_discountable_amount calculation {data["total_discountable_amount"]} not valid: should be {total_discountable_amount}'
            )
        # # Adding of additional charge in grand total
        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                f'grand_total calculation {data["grand_total"]} not valid: should be {grand_total}'
            )

        # validation for total_taxable_amount
        if total_taxable_amount != data['total_taxable_amount']:
            raise serializers.ValidationError(
                'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
                                                                                     total_taxable_amount)
            )

        # validation for total_non_taxable_amount
        if total_nontaxable_amount != data['total_non_taxable_amount']:
            raise serializers.ValidationError(
                'total_non_taxable_amount calculation {} not valid: should be {}'.format(
                    data['total_non_taxable_amount'],
                    total_nontaxable_amount)
            )

        # check subtotal , total discount , total tax and grand total
        if sub_total != data['sub_total']:
            raise serializers.ValidationError(
                'sub_total calculation not valid: should be {}'.format(sub_total)
            )
        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'], total_discount)
            )
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        return data


class CancelCustomerOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = ['id', 'order_no', 'status', 'customer', 'status_display',
                  'discount_scheme', 'total_discount', 'total_tax', 'sub_total',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'delivery_date_ad', 'delivery_date_bs', 'delivery_location', 'grand_total', 'remarks'
                  ]
        read_only_fields = ['order_no', 'customer', 'status_display',
                            'discount_scheme', 'total_discount', 'total_tax', 'sub_total',
                            'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                            'delivery_date_ad', 'delivery_date_bs', 'delivery_location', 'grand_total', 'remarks'
                            ]

    def update(self, instance, validated_data):
        if validated_data['status'] != 3:
            raise serializers.ValidationError({"message": "please end status = 3 to cancel whole order"})
        #  update instance to cancelled 
        instance.status = 3
        instance.save()
        # change status of order details
        order_details = instance.order_details.all().approved()
        for order_detail in order_details:
            # delete all sale pack type codes
            pack_type_codes = order_detail.customer_packing_types.all()
            for pack_type_code in pack_type_codes:
                pack_type_code.sale_packing_type_detail_code.all().delete()
            order_detail.customer_packing_types.all().delete()
            order_detail.cancelled = True
            order_detail.save()
        return instance


class CancelSingleOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ["cancelled", "remarks", 'item', 'qty', 'purchase_cost',
                  'sale_cost', 'discountable', 'taxable', 'tax_rate', 'tax_amount',
                  'discount_rate', 'discount_amount', 'gross_amount', 'net_amount',
                  'cancelled', 'purchase_detail', 'remarks']

    def update(self, instance, validated_data):
        # delete all sale pack type codes
        pack_type_codes = instance.customer_packing_types.all()
        for pack_type_code in pack_type_codes:
            pack_type_code.sale_packing_type_detail_code.all().delete()
        instance.customer_packing_types.all().delete()
        instance.cancelled = True
        instance.remarks = validated_data['remarks']
        instance.save()

        # update customer order master
        order_master = instance.order
        order_master.sub_total = order_master.sub_total - instance.gross_amount
        order_master.grand_total = order_master.grand_total - instance.net_amount
        prob_taxable_amount = instance.gross_amount
        if instance.discountable is True:
            order_master.total_discount = order_master.total_discount - instance.discount_amount
            order_master.total_discountable_amount = order_master.total_discountable_amount - instance.gross_amount
            prob_taxable_amount = prob_taxable_amount - instance.discount_amount
        if instance.taxable is True:
            order_master.total_tax = order_master.total_tax - instance.tax_amount
            order_master.total_taxable_amount = order_master.total_taxable_amount - prob_taxable_amount
        else:
            order_master.total_non_taxable_amount = order_master.total_taxable_amount - prob_taxable_amount
        order_master.save()
        return instance


class UpdateCustomerOrderSerializer(serializers.ModelSerializer):
    order_details = SaveOrderDetailSerializer(many=True, required=False)
    order_no = serializers.CharField(max_length=20, read_only=True)
    status = serializers.ChoiceField(choices=OrderMaster.STATUS_TYPE, read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.filter(active=True), required=False)
    total_discount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_tax = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    sub_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_discountable_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_taxable_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_non_taxable_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    delivery_date_ad = serializers.DateField(allow_null=True, required=False)
    customer_first_name = serializers.ReadOnlyField(source="customer.first_name", allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source="customer.middle_name", allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source="customer.last_name", allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = ['id', 'order_no', 'status', 'order_details', 'customer',
                  'discount_scheme', 'total_discount', 'total_tax',
                  'sub_total', 'total_discountable_amount', 'total_taxable_amount',
                  'total_non_taxable_amount', 'delivery_date_ad', 'delivery_location',
                  'grand_total', 'customer_first_name', 'customer_middle_name', 'customer_last_name', 'status_display',
                  'delivery_date_bs',
                  'remarks', 'created_by_user_name']
        read_only_fields = ['delivery_date_bs']

    def update(self, instance, validated_data):
        date_now = timezone.now()
        order_details = validated_data.pop('order_details')
        created_by = current_user.get_created_by(self.context)
        # update instance of customer order master
        instance.customer = validated_data.get('customer', instance.customer)
        instance.discount_scheme = validated_data.get('discount_scheme', instance.discount_scheme)
        instance.total_discount = validated_data.get('total_discount', instance.total_discount)
        instance.total_tax = validated_data.get('total_tax', instance.total_tax)
        instance.sub_total = validated_data.get('sub_total', instance.sub_total)
        instance.total_discountable_amount = validated_data.get('total_discountable_amount',
                                                                instance.total_discountable_amount)
        instance.total_taxable_amount = validated_data.get('total_taxable_amount', instance.total_taxable_amount)
        instance.total_non_taxable_amount = validated_data.get('total_non_taxable_amount',
                                                               instance.total_non_taxable_amount)
        instance.delivery_date_ad = validated_data.get('delivery_date_ad', instance.delivery_date_ad)
        instance.delivery_location = validated_data.get('delivery_location', instance.delivery_location)
        instance.grand_total = validated_data.get('grand_total', instance.grand_total)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.save()

        # all the order are stored in OrderDetail
        if order_details:
            for detail in order_details:
                customer_packing_types = detail.pop('customer_packing_types')
                order_detail_db = OrderDetail.objects.create(**detail, order=instance,
                                                             created_by=created_by,
                                                             created_date_ad=date_now)
                for customer_pack_type in customer_packing_types:
                    sale_pack_type_details = customer_pack_type.pop('sale_packing_type_detail_code')
                    sale_pack_type_db = SalePackingTypeCode.objects.create(
                        **customer_pack_type,
                        customer_order_detail=order_detail_db
                    )
                    for sale_pack_type_detail in sale_pack_type_details:
                        SalePackingTypeDetailCode.objects.create(
                            **sale_pack_type_detail,
                            sale_packing_type_code=sale_pack_type_db
                        )
        return instance

    def order_update_validate(self, attrs, order_master):
        grand_total = attrs.get("grand_total")
        grand_total_db = Decimal("0.00")
        order_details = attrs.get("order_details")
        order_details_db = OrderDetail.objects.filter(order=order_master)
        for order_detail_db in order_details_db:
            grand_total_db += order_detail_db.net_amount
        for order_detail in order_details:
            grand_total_db += order_detail['net_amount']
        if grand_total != grand_total_db:
            raise serializers.ValidationError({"error": f"grand_total {grand_total} does not match with backend "
                                                        f"calculation {grand_total_db}"})


class UpdateCustomerOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['id', 'purchase_cost', 'sale_cost', ]


class ApproveCustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMaster
        fields = ['id', 'approved', 'approved_by']
        read_only_fields = fields

    def update(self, instance, validated_data):
        if instance.approved:
            raise serializers.ValidationError({"msg": "This order has already been approved"})

        # paid_amount = sum(CreditClearance.objects.filter(sale_master__customer=instance.customer,
        #                                                  payment_type=1)
        #                   .values_list('total_amount', flat=True))
        #
        # refund_amount = sum(CreditClearance.objects.filter(sale_master__customer=instance.customer,
        #                                                    payment_type=2)
        #                     .values_list('total_amount', flat=True))
        #
        # total_sale_amount = sum(
        #     SaleMaster.objects.filter(customer=instance.customer, pay_type=2).values_list(
        #         'grand_total',
        #         flat=True))
        #
        # sale_return_amount = sum(
        #     SaleMaster.objects.filter(customer=instance.customer,
        #                               pay_type=2)
        #     .values_list('grand_total', flat=True))
        #
        # due_amount = total_sale_amount - sale_return_amount - paid_amount - refund_amount
        # print(due_amount)
        #
        # if instance.customer.credit_limit < (instance.grand_total + due_amount):
        #     raise serializers.ValidationError(
        #         {"msg": f"grand total : {instance.grand_total} "
        #                 f"is greater than credit limit with due : {instance.grand_total + due_amount}"})
        instance.approved = True
        approved_by = current_user.get_created_by(self.context)
        instance.approved_by = approved_by
        instance.save()

        return instance
