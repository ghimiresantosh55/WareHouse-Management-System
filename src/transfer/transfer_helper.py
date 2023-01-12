from django.db import connections
from django.db.models import F
from django.utils import timezone

from src.item.models import PackingTypeDetail, PackingType
from src.item_serialization.models import SalePackingTypeCode, SalePackingTypeDetailCode
from src.purchase.purchase_unique_id_generator import generate_purchase_no
from src.transfer.models import TransferDetail, TransferMaster
from src.transfer.purchase_serializers import SaveTransferOpeningStockSerializer
from tenant.models import Tenant


def save_transfer_data_to_branch(transfer_data):
    transfer_detail_data = transfer_data.pop("transfer_details")
    branch_id = transfer_data['branch']
    schema_name = None

    with connections['default'].cursor() as cursor:
        cursor.execute("set search_path to public")
        print("branch id : ", branch_id)
        schema_name = Tenant.objects.get(id=branch_id).schema_name
    with connections['default'].cursor() as cursor:
        time_now = timezone.now()
        cursor.execute(f"set search_path to {schema_name}")
        purchase_master_data = {
            "purchase_no": generate_purchase_no(purchase_type=3),
            "purchase_type": 3,
            "pay_type": 2,
            "sub_total": transfer_data['sub_total'],
            "grand_total": transfer_data["grand_total"],
            "remarks": "transferred from main branch",
            "purchase_details": []

        }
        for detail in transfer_detail_data:
            transfer_pack_type_codes = detail["transfer_packing_types"]
            # create_packing_type
            try:
                packing_type_detail = PackingTypeDetail.objects.get(item=detail["item"], pack_qty=detail["pack_qty"])
                packing_type = packing_type_detail.packing_type
            except PackingTypeDetail.DoesNotExist:
                try:
                    packing_type = PackingType.objects.get(name="PACK")
                except PackingType.DoesNotExist:
                    packing_type = PackingType.objects.create(
                        name="PACK",
                        short_name="PK",
                        created_by_id=1,
                        created_date_ad=time_now
                    )
                packing_type_detail = PackingTypeDetail.objects.create(
                    item_id=detail["item"],
                    packing_type=packing_type,
                    pack_qty=detail['pack_qty'],
                    created_by_id=1,
                    created_date_ad=time_now
                )
            # createing purchase detail
            purchase_detail_data = {
                "item": detail["item"],
                "item_category": detail["item_category"],
                "purchase_cost": detail["cost"],
                "qty": detail["qty"],
                "pack_qty": detail["pack_qty"],
                "gross_amount": detail["gross_amount"],
                "net_amount": detail["net_amount"],
                "packing_type": packing_type.id,
                "packing_type_detail": packing_type_detail.id,
                "sale_cost": detail["cost"],
                "pu_pack_type_codes": []

            }
            pack_no = 1
            for transfer_pack_type_code in transfer_pack_type_codes:
                sale_packing_type_detail_codes = transfer_pack_type_code.pop("sale_packing_type_detail_code")
                pu_pack_type_codes = {
                    "pack_no": pack_no,
                    "pack_type_detail_codes": []
                }
                pack_no += 1
                for sale_packing_type_detail_code in sale_packing_type_detail_codes:
                    pack_type_detail_codes_data = {
                        "code": sale_packing_type_detail_code['code']
                    }
                    pu_pack_type_codes['pack_type_detail_codes'].append(pack_type_detail_codes_data)
                purchase_detail_data["pu_pack_type_codes"].append(pu_pack_type_codes)

            purchase_master_data["purchase_details"].append(purchase_detail_data)

        serializer = SaveTransferOpeningStockSerializer(data=purchase_master_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            raise serializer.errors


def save_transfer_data(transfer_master_id):
    # transfer_detail_data = transfer_data.pop("transfer_details")
    transfer_master = TransferMaster.objects.get(id=transfer_master_id)
    transfer_detail_data = list(TransferDetail.objects.filter(
        transfer_master=transfer_master_id, cancelled=False, is_picked=True
    ).values(
        "id", "item", "pack_qty", "item_category", "cost", "qty", "gross_amount", "net_amount"
    ))

    branch_id = transfer_master.branch
    schema_name = None
    with connections['default'].cursor() as cursor:
        cursor.execute("set search_path to public")
        schema_name = Tenant.objects.get(id=branch_id).schema_name

    time_now = timezone.now()
    purchase_master_data = {
        "purchase_no": generate_purchase_no(purchase_type=3),
        "purchase_type": 3,
        "pay_type": 2,
        "sub_total": transfer_master.sub_total,
        "grand_total": transfer_master.grand_total,
        "remarks": "transferred from main branch",
        "purchase_details": []

    }
    for detail in transfer_detail_data:
        transfer_pack_type_codes = SalePackingTypeCode.objects.filter(
            transfer_detail=detail["id"]
        ).values("id")
        # create_packing_type
        with connections['default'].cursor() as cursor:
            cursor.execute(f"set search_path to {schema_name}")
            try:
                packing_type_detail = PackingTypeDetail.objects.get(item=detail["item"], pack_qty=detail["pack_qty"])
                packing_type = packing_type_detail.packing_type
            except PackingTypeDetail.DoesNotExist:
                packing_type = PackingType.objects.create(
                    name=f"{detail['item']}",
                    short_name=f"{detail['item']}",
                    created_by_id=1,
                    created_date_ad=time_now
                )
                packing_type_detail = PackingTypeDetail.objects.create(
                    item_id=detail["item"],
                    packing_type=packing_type,
                    pack_qty=detail['pack_qty'],
                    created_by_id=1,
                    created_date_ad=time_now
                )
        # createing purchase detail
        purchase_detail_data = {
            "item": detail["item"],
            "item_category": detail["item_category"],
            "purchase_cost": detail["cost"],
            "qty": detail["qty"],
            "pack_qty": detail["pack_qty"],
            "gross_amount": detail["gross_amount"],
            "net_amount": detail["net_amount"],
            "packing_type": packing_type.id,
            "packing_type_detail": packing_type_detail.id,
            "sale_cost": detail["cost"],
            "pu_pack_type_codes": []

        }
        pack_no = 1
        for transfer_pack_type_code in transfer_pack_type_codes:
            sale_packing_type_detail_codes = SalePackingTypeDetailCode.objects.filter(
                sale_packing_type_code=transfer_pack_type_code['id']
            ).values("id").annotate(code=F("packing_type_detail_code__code"))
            pu_pack_type_codes = {
                "pack_no": pack_no,
                "pack_type_detail_codes": []
            }
            pack_no += 1
            for sale_packing_type_detail_code in sale_packing_type_detail_codes:
                pack_type_detail_codes_data = {
                    "code": sale_packing_type_detail_code['code']
                }
                pu_pack_type_codes['pack_type_detail_codes'].append(pack_type_detail_codes_data)
            purchase_detail_data["pu_pack_type_codes"].append(pu_pack_type_codes)

        purchase_master_data["purchase_details"].append(purchase_detail_data)

    with connections['default'].cursor() as cursor:
        cursor.execute(f"set search_path to {schema_name}")
        serializer = SaveTransferOpeningStockSerializer(data=purchase_master_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            raise serializer.errors
