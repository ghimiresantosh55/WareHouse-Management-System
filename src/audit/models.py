from django.db import models

from src.core_app.models import CreateInfoModel
from src.item.models import Item
from src.item_serialization.models import PackingTypeDetailCode


class Audit(CreateInfoModel):
    audit_no = models.CharField(max_length=20, unique=True, help_text="Audit no. should be max. of 10 characters")
    remarks = models.CharField(max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")
    is_finished = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.id}: {self.audit_no}"


class AuditDetail(CreateInfoModel):
    DETAIL_TYPES = [
        (1, "AVAILABLE"),
        (2, "AUDITED"),
        (3, "MISSING")
    ]

    audit = models.ForeignKey(Audit, related_name='audit_details', on_delete=models.PROTECT)
    detail_type = models.IntegerField(choices=DETAIL_TYPES)
    packing_type_detail_code = models.ForeignKey(PackingTypeDetailCode, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.id} : {self.packing_type_detail_code} : {self.detail_type}"


class ItemAudit(CreateInfoModel):
    audit_no = models.CharField(max_length=20, unique=True, help_text="Audit no. should be max. of 10 characters")
    remarks = models.CharField(max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="item_audit")

    def __str__(self):
        return f"{self.id} : {self.audit_no}"


class ItemAuditDetail(CreateInfoModel):
    TAG_STATUS = (
        (1, "FOUND"),
        (2, "MISSING")
    )
    audit_status = models.PositiveIntegerField(choices=TAG_STATUS, help_text="Audit status of an item during audit")
    packing_type_detail_code = models.ForeignKey(PackingTypeDetailCode, on_delete=models.PROTECT)
    item_audit = models.ForeignKey(ItemAudit, on_delete=models.PROTECT, related_name="item_audit_details")

    def __str__(self):
        return f"{self.id}"

