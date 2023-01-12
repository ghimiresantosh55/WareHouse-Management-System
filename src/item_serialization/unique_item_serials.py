from .models import PackingTypeCode, PackingTypeDetailCode


def generate_packtype_serial():
    count = PackingTypeCode.objects.filter(ref_packing_type_code__isnull=True).count() + 1
    return "PK-" + str(count).zfill(10)


def generate_packtype_detail_serial():
    count = PackingTypeDetailCode.objects.filter(ref_packing_type_detail_code__isnull=True).count() + 1
    return "SE-" + str(count).zfill(10)


def packing_type_detail_code_list(pack_qty, pack_type_code, created_by
                                  , created_date_ad) -> list:
    count = PackingTypeDetailCode.objects.filter(ref_packing_type_detail_code__isnull=True).count() + 1
    serial_nos = []
    for x in range(pack_qty):
        serial_nos.append(PackingTypeDetailCode(code="SE-" + str(count).zfill(10),
                                                pack_type_code_id=pack_type_code,
                                                created_by_id=created_by,
                                                created_date_ad=created_date_ad,
                                                created_date_bs='NA'))
        count += 1
    return serial_nos
