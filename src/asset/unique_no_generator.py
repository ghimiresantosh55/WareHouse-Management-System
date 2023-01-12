from .models import Asset, AssetDispatch

ORDER_NO_LENGTH = 7


def generate_asset_re_serial():
    order_count = Asset.objects.count()
    max_id = str(order_count + 1)
    unique_id = "RE" + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id


def generate_asset_dispatch_no_serial(dispatch_type: int):
    if dispatch_type == 1:
        order_count = AssetDispatch.objects.filter(dispatch_info=1).count()
        max_id = str(order_count + 1)
        unique_id = "AD" + "-" + max_id.zfill(ORDER_NO_LENGTH)
        return unique_id
    else:
        order_count = AssetDispatch.objects.filter(dispatch_info=2).count()
        max_id = str(order_count + 1)
        unique_id = "ADR" + "-" + max_id.zfill(ORDER_NO_LENGTH)
        return unique_id
