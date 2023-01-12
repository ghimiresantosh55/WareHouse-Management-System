from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import OuterRef
from django.db.models import Sum, F, Subquery, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.custom_lib.functions import current_user
from src.purchase.models import PurchaseMaster
from .models import PartyPayment, PartyPaymentDetail
from .reciept_unique_id_generator import get_receipt_no

User = get_user_model()


class SupplierPartyPayment:
    supplier = None
    purchase_masters = PurchaseMaster.objects.none()
    party_payment_details = []
    current_user = User.objects.none()
    created_date_ad = None

    def __init__(self, supplier, party_payment_details):
        self.supplier = supplier
        self.party_payment_details = party_payment_details
        self.set_purchase_masters()

    def save_party_payment(self, context):
        self.current_user = current_user.get_created_by(context)
        self.created_date_ad = timezone.now()

        for purchase_master in self.purchase_masters:

            if len(self.party_payment_details) <= 0:
                break

            remaining_due = purchase_master['due_amount']
            party_payment_master_data = {
                "purchase_master": PurchaseMaster.objects.get(id=purchase_master['id']),
                "payment_type": 1,
                "receipt_no": get_receipt_no(),
                "total_amount": Decimal("0.00"),
                "party_payment_details": []
            }

            for i in range(len(self.party_payment_details)):
                if remaining_due >= self.party_payment_details[i - 1]['amount']:
                    remaining_due = remaining_due - self.party_payment_details[i - 1]['amount']
                    party_payment_detail_data = {
                        "payment_mode": self.party_payment_details[i - 1]['payment_mode'],
                        "amount": self.party_payment_details[i - 1]['amount'],
                        "remarks": self.party_payment_details[i - 1]['remarks']
                    }
                    party_payment_master_data['party_payment_details'].append(party_payment_detail_data)
                    party_payment_master_data['total_amount'] += party_payment_detail_data['amount']
                    self.party_payment_details.pop(i - 1)
                else:
                    self.party_payment_details[i - 1]['amount'] -= remaining_due
                    party_payment_detail_data = {
                        "payment_mode": self.party_payment_details[i - 1]['payment_mode'],
                        "amount": remaining_due,
                        "remarks": self.party_payment_details[i - 1]['remarks']
                    }
                    party_payment_master_data['party_payment_details'].append(party_payment_detail_data)
                    party_payment_master_data['total_amount'] += party_payment_detail_data['amount']
                    break

            # saving party payment for purchase master
            party_payment_details = party_payment_master_data.pop('party_payment_details')
            party_payment_master_db = PartyPayment.objects.create(
                **party_payment_master_data, created_by=self.current_user,
                created_date_ad=self.created_date_ad
            )

            for party_payment_detail in party_payment_details:
                PartyPaymentDetail.objects.create(
                    **party_payment_detail, party_payment=party_payment_master_db,
                    created_by=self.current_user, created_date_ad=self.created_date_ad
                )

    def set_purchase_masters(self):
        purchase_return_amount = PurchaseMaster.objects.filter(ref_purchase=OuterRef("id")).annotate(
            purchase_return_amount=Coalesce(Sum('total_amount'), Decimal("0.00"))
        ).values('purchase_return_amount')

        party_payment_amount = PartyPayment.objects.filter(purchase_master=OuterRef("id"), payment_type=1).annotate(
            party_payment_amount=Coalesce(Sum('total_amount'), Decimal("0.00"))
        ).values('party_payment_amount')

        party_payment_refund_amount = PartyPayment.objects.filter(purchase_master=OuterRef("id"),
                                                                  payment_type=2).annotate(
            party_payment_refund_amount=Coalesce(Sum('total_amount'), Decimal("0.00"))
        ).values('party_payment_refund_amount')

        self.purchase_masters = PurchaseMaster.objects.filter(
            pay_type=2, supplier=self.supplier
        ).annotate(
            due_amount=(F("grand_total") - Subquery(purchase_return_amount, output_field=DecimalField())) - (
                    Subquery(party_payment_amount, output_field=DecimalField
                             ) - Subquery(party_payment_refund_amount, output_field=DecimalField())
            )
        ).filter(due_amount__gt=0).values("id", "due_amount")
