from django.db.models import Count

from src.item_serialization.models import PackingTypeDetailCode
from .models import AuditDetail


def generate_audit(audit):
    audited_audit_details = PackingTypeDetailCode.objects.filter(
        auditdetail__audit=audit, auditdetail__detail_type=2
    ).distinct("id").order_by("id").values("id")
    available_items = PackingTypeDetailCode.objects.filter(packingtypedetailcode__isnull=True).annotate(
        ref_count=Count('pack_type_detail_code_of_sale') % 2).filter(ref_count=0).order_by("id").values(
        "id"
    )
    missing_audit_details = available_items.difference(audited_audit_details)
    #     Save all available items
    for available_item in available_items:
        AuditDetail.objects.create(
            audit=audit,
            detail_type=1,
            packing_type_detail_code=PackingTypeDetailCode.objects.get(id=available_item['id']),
            created_date_ad=audit.created_date_ad,
            created_by=audit.created_by
        )
    # saving missing audit details
    for missing_audit_detail in missing_audit_details:
        AuditDetail.objects.create(
            audit=audit,
            detail_type=3,
            packing_type_detail_code=PackingTypeDetailCode.objects.get(id=missing_audit_detail['id']),
            created_date_ad=audit.created_date_ad,
            created_by=audit.created_by
        )
