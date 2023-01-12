from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.custom_lib.functions import fiscal_year
from src.item_serialization.models import PackingTypeDetailCode, PackingTypeCode
from src.item_serialization.unique_item_serials import generate_packtype_serial, packing_type_detail_code_list
from src.purchase.models import PurchaseDetail, PurchaseMaster
from src.purchase.purchase_unique_id_generator import generate_purchase_no, generate_batch_no

User = get_user_model()


class SaveTransferPurchaseOpeningStockPackingTypeDetailCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTypeDetailCode
        exclude = ["pack_type_code"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveTransferPurchaseOpeningStockPackingTypeCodeSerializer(serializers.ModelSerializer):
    pack_type_detail_codes = SaveTransferPurchaseOpeningStockPackingTypeDetailCodeSerializer(
        many=True, required=False
    )
    pack_no = serializers.IntegerField(write_only=True)

    class Meta:
        model = PackingTypeCode
        exclude = ["purchase_order_detail", "purchase_detail"]
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'code']
        extra_kwargs = {
            'pack_no': {'write_only': True}
        }


class SaveTransferPurchaseOpeningStockDetailSerializer(serializers.ModelSerializer):
    pu_pack_type_codes = SaveTransferPurchaseOpeningStockPackingTypeCodeSerializer(many=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'item', 'item_category', 'purchase_cost', 'sale_cost',
                  'qty', 'pack_qty', 'packing_type', 'packing_type_detail',
                  'taxable', 'tax_rate', 'tax_amount', 'discountable', 'expirable',
                  'discount_rate', 'discount_amount', 'discount_amount', 'gross_amount',
                  'gross_amount', 'net_amount', 'expiry_date_ad', 'expiry_date_bs',
                  'batch_no', 'item_name', 'item_category_name', 'created_by_user_name',
                  'pu_pack_type_codes']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs', 'batch_no']


class SaveTransferOpeningStockSerializer(serializers.ModelSerializer):
    purchase_details = SaveTransferPurchaseOpeningStockDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = ['id', 'purchase_no', 'purchase_type', 'pay_type',
                  'sub_total', 'total_discount', 'discount_rate', 'discount_scheme',
                  'total_discountable_amount', 'total_taxable_amount', 'total_non_taxable_amount',
                  'total_tax', 'grand_total', 'supplier', 'bill_no',
                  'bill_date_ad', 'bill_date_bs', 'chalan_no', 'remarks',
                  'purchase_details', 'created_by_user_name']
        read_only_fields = ['created_by', 'created_date_ad', 'pay_type',
                            'created_date_bs', 'purchase_no', 'purchase_type',
                            'bill_data_bs']

    def create(self, validated_data):
        created_date_ad = timezone.now()
        created_by = User.objects.get(id=1)
        purchase_no = generate_purchase_no(purchase_type=3)
        purchase_details = validated_data.pop('purchase_details')
        purchase_type = 3  # 3 => OpeningStock

        # fiscal sessions
        fiscal_year_ad_short = fiscal_year.get_fiscal_year_code_ad()
        fiscal_year_bs_short = fiscal_year.get_fiscal_year_code_bs()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=fiscal_year_ad_short)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=fiscal_year_bs_short)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {
                    "fiscal_year": "please set fiscal session ad and fiscal session bs in core app"
                }
            )
        purchase_master = PurchaseMaster.objects.create(
            **validated_data, purchase_type=purchase_type, purchase_no=purchase_no,
            created_by=created_by, created_date_ad=created_date_ad,
            pay_type=1,
            fiscal_session_ad=fiscal_session_ad, fiscal_session_bs=fiscal_session_bs
        )
        if not purchase_details:
            raise serializers.ValidationError({'purchase_details': 'please provide purchase details'})
        for purchase_detail in purchase_details:
            pack_type_codes = purchase_detail.pop('pu_pack_type_codes')
            batch_no = generate_batch_no()
            purchase_detail_db = PurchaseDetail.objects.create(
                **purchase_detail, purchase=purchase_master, batch_no=batch_no,
                created_date_ad=created_date_ad,
                created_by=created_by
            )
            len_of_pack_type_code = len(pack_type_codes)
            ref_len_pack_type_code = int(
                purchase_detail['qty'] / purchase_detail['packing_type_detail'].pack_qty)
            if len_of_pack_type_code != ref_len_pack_type_code:
                raise serializers.ValidationError({"message": "pack type codes not enough"})
            for pack_type_code in pack_type_codes:
                pack_type_detail_codes = pack_type_code.pop('pack_type_detail_codes')

                code = generate_packtype_serial()
                pack_type = PackingTypeCode.objects.create(
                    code=code,
                    purchase_detail=purchase_detail_db,
                    created_by=created_by,
                    created_date_ad=created_date_ad
                )
                if pack_type_detail_codes:
                    if len(pack_type_detail_codes) != int(purchase_detail['packing_type_detail'].pack_qty):
                        raise serializers.ValidationError({"message": "packing type detail codes count does nto match"})
                    for pack_type_detail_code in pack_type_detail_codes:
                        PackingTypeDetailCode.objects.create(
                            code=pack_type_detail_code['code'],
                            pack_type_code=pack_type,
                            created_by=created_by,
                            created_date_ad=created_date_ad
                        )
                else:
                    pack_qty = int(purchase_detail['packing_type_detail'].pack_qty)

                    pack_type_detail_codes_data = packing_type_detail_code_list(pack_qty=pack_qty,
                                                                                pack_type_code=pack_type.id,
                                                                                created_by=created_by.id,
                                                                                created_date_ad=created_date_ad)
                    PackingTypeDetailCode.objects.bulk_create(
                        pack_type_detail_codes_data
                    )
        return purchase_master
