from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _

from src.chalan.models import ChalanDetail, ChalanMaster
from src.core_app.models import CreateInfoModel
from src.customer_order.models import OrderDetail
from src.department_transfer.models import DepartmentTransferDetail
from src.ppb.models import TaskDetail
from src.purchase.models import PurchaseDetail, PurchaseOrderDetail
from src.sale.models import SaleDetail
from src.transfer.models import TransferDetail
from src.warehouse_location.models import Location


class PackingTypeCode(CreateInfoModel):
    code = models.CharField(_("Packing Type Serial No"), max_length=20, help_text="max-20")
    purchase_detail = models.ForeignKey(PurchaseDetail, null=True, blank=True, verbose_name=_("Purchase Detail"),
                                        on_delete=models.PROTECT, related_name="pu_pack_type_codes")
    purchase_order_detail = models.ForeignKey(PurchaseOrderDetail, null=True, blank=True,
                                              verbose_name=_("Purchase Order Detail"), on_delete=models.PROTECT,
                                              related_name="po_pack_type_codes")
    location = models.ForeignKey(Location, verbose_name=_("Pack Type Location"), on_delete=models.PROTECT,
                                 related_name="location_pack_codes", null=True, blank=True)
    qty = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    ref_packing_type_code = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.id} : {self.code}"


class PackingTypeDetailCode(CreateInfoModel):
    code = models.CharField(_("Packing Type Detail Serail No"), max_length=20, help_text="max-20")
    pack_type_code = models.ForeignKey(PackingTypeCode, verbose_name=_("Packing Type Code"), on_delete=models.PROTECT,
                                       related_name="pack_type_detail_codes")
    ref_packing_type_detail_code = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.id} : {self.code}"


class RfidTag(CreateInfoModel):
    code = models.CharField(_("Rfid Tag Key Code"), max_length=255, help_text="max-20", unique=True)
    pack_type_detail_code = models.OneToOneField(PackingTypeDetailCode, verbose_name=_("Rfid Tag Code"),
                                                 on_delete=models.PROTECT,
                                                 related_name="rfid_tag_codes")
    last_seen_dt = models.DateTimeField()

    def __str__(self):
        return f"{self.id}: {self.code}"


class SalePackingTypeCode(models.Model):
    packing_type_code = models.ForeignKey(PackingTypeCode, verbose_name=_("sale packing type code"),
                                          on_delete=models.PROTECT, related_name="pack_type_code_of_sale")
    sale_detail = models.ForeignKey(SaleDetail, related_name="sale_packing_type_code", null=True, blank=True,
                                    verbose_name=_("Sale Detail"), on_delete=models.PROTECT)
    customer_order_detail = models.ForeignKey(
        OrderDetail, null=True, blank=True, verbose_name=_("Customer order detail"), on_delete=models.PROTECT,
        related_name="customer_packing_types"
    )
    chalan_detail = models.ForeignKey(
        ChalanDetail, null=True, blank=True, verbose_name=_('Chalan Detail'), on_delete=models.PROTECT,
        related_name="chalan_packing_types"
    )
    transfer_detail = models.ForeignKey(
        TransferDetail, null=True, blank=True, verbose_name=_('Transfer Detail'), on_delete=models.PROTECT,
        related_name="transfer_packing_types"
    )
    department_transfer_detail = models.ForeignKey(
        DepartmentTransferDetail, null=True, blank=True, verbose_name=_('Department Transfer Detail'),
        on_delete=models.PROTECT,
        related_name="department_transfer_packing_types"
    )
    task_detail = models.ForeignKey(TaskDetail, on_delete=models.PROTECT, null=True, blank=True, related_name="task_packing_type_codes")
    qty = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    ref_sale_packing_type_code = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)


class SalePackingTypeDetailCode(models.Model):
    sale_packing_type_code = models.ForeignKey(SalePackingTypeCode, on_delete=models.PROTECT,
                                               related_name="sale_packing_type_detail_code")
    packing_type_detail_code = models.ForeignKey(PackingTypeDetailCode, on_delete=models.PROTECT,
                                                 related_name="pack_type_detail_code_of_sale")

    ref_sale_packing_type_detail_code = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
