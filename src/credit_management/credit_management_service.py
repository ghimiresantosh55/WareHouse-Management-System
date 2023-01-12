from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Sum, OuterRef, F, Subquery, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.custom_lib.functions import current_user
from src.sale.models import SaleMaster
from .models import CreditClearance, CreditPaymentDetail
from .reciept_unique_id_generator import get_receipt_no

User = get_user_model()


class CustomerCreditClearance:
    customer = None
    sale_masters = SaleMaster.objects.none()
    credit_payment_details = []
    current_user = User.objects.none()
    created_date_ad = None

    def __init__(self, customer, credit_payment_details):
        self.credit_payment_details = []
        self.customer = customer
        self.credit_payment_details = credit_payment_details
        self.set_sale_masters()

    def save_credit_clearance(self, context):
        self.current_user = current_user.get_created_by(context)
        self.created_date_ad = timezone.now()

        for sale_master in self.sale_masters:

            if len(self.credit_payment_details) <= 0:
                break

            remaining_due = sale_master['due_amount']
            credit_clearance_main_data = {
                "sale_master": SaleMaster.objects.get(id=sale_master['id']),
                "payment_type": 1,
                "receipt_no": get_receipt_no(),
                "total_amount": Decimal("0.00"),
                "credit_payment_details": []
            }

            for i in range(len(self.credit_payment_details)):
                if remaining_due >= self.credit_payment_details[i - 1]['amount']:
                    remaining_due = remaining_due - self.credit_payment_details[i - 1]['amount']
                    credit_payment_details_data = {
                        "payment_mode": self.credit_payment_details[i - 1]['payment_mode'],
                        "amount": self.credit_payment_details[i - 1]['amount'],
                        "remarks": self.credit_payment_details[i - 1]['remarks']
                    }
                    credit_clearance_main_data['credit_payment_details'].append(credit_payment_details_data)
                    credit_clearance_main_data['total_amount'] += credit_payment_details_data['amount']
                    self.credit_payment_details.pop(i - 1)
                else:
                    self.credit_payment_details[i - 1]['amount'] -= remaining_due
                    credit_payment_details_data = {
                        "payment_mode": self.credit_payment_details[i - 1]['payment_mode'],
                        "amount": remaining_due,
                        "remarks": self.credit_payment_details[i - 1]['remarks']
                    }
                    credit_clearance_main_data['credit_payment_details'].append(credit_payment_details_data)
                    credit_clearance_main_data['total_amount'] += credit_payment_details_data['amount']
                    break

            # saving credit clearance for sale master
            credit_payment_details = credit_clearance_main_data.pop('credit_payment_details')
            credit_clearance_master_db = CreditClearance.objects.create(
                **credit_clearance_main_data, created_by=self.current_user,
                created_date_ad=self.created_date_ad
            )

            for credit_payment_detail in credit_payment_details:
                CreditPaymentDetail.objects.create(
                    **credit_payment_detail, credit_clearance=credit_clearance_master_db,
                    created_by=self.current_user, created_date_ad=self.created_date_ad
                )

    def set_sale_masters(self):

        sale_return_amount = SaleMaster.objects.filter(ref_sale_master=OuterRef("id")).values(
            "ref_sale_master").annotate(
            sale_return_amount=Coalesce(Sum('total_amount'), Decimal("0.00"))
        ).values('sale_return_amount')

        credit_clearance_amount = CreditClearance.objects.filter(
            sale_master=OuterRef("id"), payment_type=1
        ).values("sale_master").annotate(
            credit_clearance_amount=Coalesce(Sum('total_amount'), Decimal("0.00"))
        ).values('credit_clearance_amount')

        credit_clearance_refund_amount = CreditClearance.objects.filter(
            sale_master=OuterRef("id"),
            payment_type=2
        ).values("sale_master").annotate(
            credit_clearance_refund_amount=Coalesce(Sum('total_amount'), Decimal("0.00"))
        ).values('credit_clearance_refund_amount')

        self.sale_masters = SaleMaster.objects.filter(
            pay_type=2, customer=self.customer, ref_sale_master__isnull=True
        ).annotate(
            due_amount=(F("grand_total") - Subquery(sale_return_amount, output_field=DecimalField())) - (
                    Subquery(credit_clearance_amount, output_field=DecimalField
                             ) - Subquery(credit_clearance_refund_amount, output_field=DecimalField())
            )
        ).filter(due_amount__gt=0).values("id", "due_amount")
