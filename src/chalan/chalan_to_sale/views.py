from decimal import Decimal

from django.db.models import Prefetch, Sum, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.generics import RetrieveAPIView

from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from .serializers import ChalanMasterSummarySaleSerializer
from ..models import ChalanMaster, ChalanDetail


class SummaryChalanSaleMasterApiView(RetrieveAPIView):
    queryset = ChalanMaster.objects.select_related(
        "customer", "discount_scheme"
    ).prefetch_related(
        Prefetch(
            'chalan_details',
            queryset=ChalanDetail.objects.annotate(
                returned_qty=Coalesce(
                    Sum('chalandetail__qty', output_field=DecimalField()), Decimal("0.00")
                )
            ).prefetch_related(
                Prefetch(
                    "chalan_packing_types",
                    queryset=SalePackingTypeCode.objects.filter(
                        sale_packing_type_detail_code__salepackingtypedetailcode__isnull=True
                    ).distinct().prefetch_related(
                        Prefetch(
                            "sale_packing_type_detail_code",
                            queryset=SalePackingTypeDetailCode.objects.filter(salepackingtypedetailcode__isnull=True)
                        )
                    )
                )
            )
        ),
    )
    serializer_class = ChalanMasterSummarySaleSerializer
