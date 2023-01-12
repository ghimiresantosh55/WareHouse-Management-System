from src.sale.models import SaleMaster, SalePrintLog
from rest_framework import serializers

from src.sale.models import SaleMaster, SalePrintLog


class IRDLogSerializer(serializers.ModelSerializer):
    printed_by = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    printed_time = serializers.DateTimeField(source='created_date_ad', read_only=True, format="%H:%M:%S")
    printed_date = serializers.DateTimeField(source='created_date_ad', read_only=True, format="%Y-%m-%d")

    class Meta:
        model = SalePrintLog
        exclude = ['id', 'created_date_ad', 'sale_master', 'created_date_bs', 'created_by']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['printed_by']:
            ret['is_printed'] = True
        return ret


# for materialized purchase_order_view report
class MaterialViewReportSerializer(serializers.ModelSerializer):
    ird_log = serializers.SerializerMethodField()
    bill_date = serializers.DateTimeField(source='created_date_ad', read_only=True, format="%Y-%m-%d")
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    customer_pan_no = serializers.ReadOnlyField(source='customer.pan_vat_no', allow_null=True)
    bill_by = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = SaleMaster
        exclude = ['id', 'sub_total', 'discount_rate', 'total_discountable_amount', 'pay_type',
                   'total_non_taxable_amount', 'total_discount', 'ref_by', 'total_tax', 'sale_type', 'created_date_bs',
                   'remarks', 'discount_scheme', 'ref_sale_master', 'ref_order_master', 'customer', 'created_by']

    def get_ird_log(self, sale_master):
        try:
            report_log = SalePrintLog.objects.filter(sale_master=sale_master.id).earliest("created_date_ad")
        except:
            return []

        # print(report_log)
        serializers = IRDLogSerializer(report_log)
        # print(serializer.data)
        return serializers.data


class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleMaster
        fields = "__all__"
        # exclude = ['id','created_date_ad', 'sale_master','created_date_bs','created_by']
