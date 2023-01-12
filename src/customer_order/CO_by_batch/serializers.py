import decimal
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from src.custom_lib.functions import current_user
from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from src.item_serialization.services import pack_and_serial_info
from ..models import OrderDetail
from ..models import OrderMaster
from ..order_unique_id_generator import generate_customer_order_no
from ...item_serialization.services.pack_and_serial_info import available_pack_qty_non_serializable
from ...purchase.services.stock_analysis import get_batch_stock


class SaveOrderDetailByBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        exclude = ['order', 'device_type', 'app_type']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']
        extra_kwargs = {
            "purchase_detail": {"required": True}
        }


class SaveCustomerOrderByBatchSerializer(serializers.ModelSerializer):
    order_details = SaveOrderDetailByBatchSerializer(many=True)

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
            by_batch=True,
            **validated_data, created_date_ad=date_now,
            created_by=created_by
        )

        for detail in order_details:
            OrderDetail.objects.create(**detail, order=order_master, created_by=created_by,
                                       created_date_ad=date_now)

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

            # check items are same or not for customer order and batch
            customer_order_item = customer_order_detail['item']
            batch_item = customer_order_detail['purchase_detail'].item
            if customer_order_item != batch_item:
                raise serializers.ValidationError({"item": f"item in customer order {customer_order_item.id} is not "
                                                           f"batch item {batch_item.id}"})

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

    ##TODO: validate 
    def validate_order_details(self, order_details):

        # validation for order detail qty
        batches = []
        for order in order_details:
            order_qty = order['qty']
            batch_id = order['purchase_detail'].id
            item = get_batch_stock().get(item=order['item'], id=batch_id)
            # check batch uniqueness
            if batch_id in batches:
                raise serializers.ValidationError({"error": "please ensure unique batches"})
            else:
                batches.append(batch_id)

            # check item qty
            if item['remaining_qty'] < order_qty:
                raise serializers.ValidationError(
                    {
                        "error": f"item order qty : {order_qty} is greater than remaining qty : {item['remaining_qty']}"
                    }
                )

        return order_details


class SaveCustomerPackingTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePackingTypeDetailCode
        fields = ['id', 'packing_type_detail_code']


class SaveCustomerPackingTypesSerializer(serializers.ModelSerializer):
    sale_packing_type_detail_code = SaveCustomerPackingTypeDetailsSerializer(many=True)

    class Meta:
        model = SalePackingTypeCode
        fields = ['id', 'packing_type_code', 'sale_packing_type_detail_code', 'qty']
        extra_kwargs = {
            'qty': {'required': True}
        }


class SaveAndVerifyCustomerPackingTypesSerializer(serializers.Serializer):
    customer_order_detail = serializers.PrimaryKeyRelatedField(
        queryset=OrderDetail.objects.filter(order__status=1, order__by_batch=True, picked=False)
    )
    customer_packing_types = SaveCustomerPackingTypesSerializer(many=True)

    def to_representation(self, instance):

        order_detail = OrderDetail.objects.get(id=instance['customer_order_detail'].id)

        quantize_places = Decimal(10) ** -2

        customer_order_detail_data = {
            "id": order_detail.id,
            "qty": str(Decimal(order_detail.qty).quantize(quantize_places)),
            "item_name": str(order_detail.item.name),
            "purchase_cost": str(Decimal(order_detail.purchase_cost).quantize(quantize_places)),
            "sale_cost": str(Decimal(order_detail.sale_cost).quantize(quantize_places)),
            "taxable": order_detail.taxable,
            "tax_rate": str(Decimal(order_detail.tax_rate).quantize(quantize_places)),
            "tax_amount": str(Decimal(order_detail.tax_amount).quantize(quantize_places)),
            "discountable": order_detail.discountable,
            "discount_rate": str(Decimal(order_detail.discount_rate).quantize(quantize_places)),
            "discount_amount": str(Decimal(order_detail.discount_amount).quantize(quantize_places)),
            "gross_amount": str(Decimal(order_detail.gross_amount).quantize(quantize_places)),
            "net_amount": str(Decimal(order_detail.net_amount).quantize(quantize_places)),
            "cancelled": order_detail.cancelled,
            "remarks": order_detail.remarks,
            "picked": order_detail.picked
        }

        return customer_order_detail_data

    def create(self, validated_data):
        order_detail = validated_data['customer_order_detail']
        order_detail.picked = True
        order_detail.save()
        customer_packing_types = validated_data['customer_packing_types']
        order_qty = order_detail.qty
        serial_no_count = 0
        for customer_pack_type in customer_packing_types:
            sale_pack_type_details = customer_pack_type['sale_packing_type_detail_code']
            sale_pack_type_db = SalePackingTypeCode.objects.create(
                packing_type_code=customer_pack_type['packing_type_code'],
                customer_order_detail=order_detail
            )
            for sale_pack_type_detail in sale_pack_type_details:
                SalePackingTypeDetailCode.objects.create(
                    packing_type_detail_code=sale_pack_type_detail['packing_type_detail_code'],
                    sale_packing_type_code=sale_pack_type_db
                )
                serial_no_count += 1
        if order_qty != serial_no_count:
            raise serializers.ValidationError(
                {"error": f"order qty {order_qty} is not equal to serial_nos scanned {serial_no_count}"})
        return validated_data

    def validate(self, attrs):
        customer_packing_types = attrs['customer_packing_types']
        for customer_pack_type in customer_packing_types:
            packing_type_code = customer_pack_type['packing_type_code']
            if attrs['customer_order_detail'].item.is_serializable is True:
                available_pack = pack_and_serial_info.find_available_serial_nos(packing_type_code.id)
                if not available_pack.exists():
                    raise serializers.ValidationError({"message": f"{packing_type_code.code} is not available"})
                sale_pack_type_details = customer_pack_type['sale_packing_type_detail_code']
                for sale_pack_type_detail in sale_pack_type_details:
                    serial_no_code = sale_pack_type_detail['packing_type_detail_code']
                    available_serial_no = pack_and_serial_info.find_available_serial_no(serial_no_code.id)
                    if not available_serial_no:
                        raise serializers.ValidationError({"message": f"{serial_no_code.code} is not available"})
            else:
                pack = available_pack_qty_non_serializable(customer_pack_type['packing_type_code'].id)
                remaining_qty = pack['qty'] - pack['sold_qty'] + pack['return_qty']
                if customer_pack_type['qty'] > remaining_qty:
                    raise serializers.ValidationError(
                        {"error": f"packet qty {customer_pack_type['qty']} more than remaining qty of packet {remaining_qty}"}
                    )

        super(SaveAndVerifyCustomerPackingTypesSerializer, self).validate(attrs)


class UpdateCustomerDetailsByBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = '__all__'

        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class UpdateCustomerOrderByBatchSerializer(serializers.ModelSerializer):
    order_details = UpdateCustomerDetailsByBatchSerializer(many=True, required=False)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def update(self, instance, validated_data):
        current_date = timezone.now()
        self.order_update_validate(validated_data, instance)

        try:
            order_details = validated_data.pop('order_details')
        except KeyError:
            order_details = []

        created_by = self.context.get('request').user

        instance.sub_total = validated_data.get("sub_total", instance.sub_total)
        instance.discount_scheme = validated_data.get("discount_scheme", instance.discount_scheme)
        instance.total_discount = validated_data.get("total_discount", instance.total_discount)
        instance.total_discountable_amount = validated_data.get("total_discountable_amount",
                                                                instance.total_discountable_amount)
        instance.total_taxable_amount = validated_data.get("total_taxable_amount", instance.total_taxable_amount)
        instance.total_non_taxable_amount = validated_data.get("total_non_taxable_amount",
                                                               instance.total_non_taxable_amount)
        instance.total_tax = validated_data.get("total_tax", instance.total_tax)
        instance.grand_total = validated_data.get("grand_total", instance.grand_total)
        instance.customer = validated_data.get("customer", instance.customer)
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.save()

        for order_detail in order_details:
            OrderDetail.objects.create(
                **order_detail, order=instance,
                created_by=created_by,
                created_date_ad=current_date
            )

        return instance

    def order_update_validate(self, attrs, order_master):
        grand_total = attrs.get("grand_total")
        grand_total_db = Decimal("0.00")
        order_details = attrs.get("order_details")
        order_details_db = OrderDetail.objects.filter(order=order_master,
                                                      cancelled=False)
        for order_detail_db in order_details_db:
            grand_total_db += order_detail_db.net_amount
        for order_detail in order_details:
            grand_total_db += order_detail['net_amount']
        if grand_total != grand_total_db:
            raise serializers.ValidationError({"error": f"grand_total {grand_total} does not match with backend "
                                                        f"calculation {grand_total_db}"})
