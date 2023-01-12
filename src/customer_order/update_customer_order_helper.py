from .models import OrderDetail


class UpdateCustomerOrder:
    order_detail_data = {}
    order_master_data = {}
    order_detail = None
    order_master = None

    def __init__(self, order_detail: OrderDetail, order_detail_data, order_master_data):
        self.order_detail = order_detail
        self.order_detail_data = order_detail_data
        self.order_master_data = order_master_data
        self.order_master = order_detail.order
        self.update_order_detail()
        self.update_order_master()

    def update_order_master(self):
        self.order_master.objects.update(**self.order_master_data)

    def update_order_detail(self):
        self.order_detail.objects.update(**self.order_detail_data)
