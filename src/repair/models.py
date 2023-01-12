from django.db import models
from simple_history import register
from src.core_app.models import CreateInfoModel
from src.item_serialization.models import PackingTypeDetailCode
from src.sale.models import SaleMaster, SaleDetail
from src.item.models import  Item
from src.user.models import User
from src.customer.models import Customer
import nepali_datetime


class Repair(CreateInfoModel):
    REPAIR_STATUS = (
        (1, "PENDING"),
        (2, "COMPLETED"),
        (3, "CANCELED"),
       
    )
    customer = models.ForeignKey(Customer,  on_delete=models.PROTECT, null=True, blank=True, help_text="null= True, blank = true")
    repair_status = models.PositiveIntegerField(choices = REPAIR_STATUS, default=1,
                                            help_text="where 1=PENDING, 2= COMPLETED, 3=CANCELED")
    expected_date_to_repair_ad= models.DateField(blank= True, null= True,help_text="Expected Date To Repair AD, blank = True")
    expected_date_to_repair_bs = models.CharField(max_length=10,blank = True, help_text="Expected Date To Repair BS, blank = True")
    total_repair_cost= models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can have max value "
                                                              "upto=9999999999.99 and default=0.0")

    def save(self, *args, **kwargs):
        if self.expected_date_to_repair_ad is not None:
            expected_date_to_repair_bs = nepali_datetime.date.from_datetime_date(self.expected_date_to_repair_ad)
            self. expected_date_to_repair_bs =  expected_date_to_repair_bs
        super().save(*args, **kwargs)
    
    def __str__(self):
        return "id {}".format(self.id)



class RepairDetail(CreateInfoModel):
    sale = models.ForeignKey(SaleMaster, on_delete=models.PROTECT, related_name= "repair_sale_details", null=True,blank=True, help_text="null= True, blank = true")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null= True,  blank=True,  help_text="null= True, blank= True")
    repair= models.ForeignKey(Repair, on_delete=models.PROTECT,related_name="repair_details")
    sale_detail= models.ForeignKey(SaleDetail, on_delete=models.PROTECT, null=True,blank=True, help_text="null= True, blank = true") 
    problem_description = models.CharField(max_length=200, blank = True, help_text="max length can be upto 200 and blank = true")
    repair_cost= models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can have max value "
                                                              "upto=9999999999.99 and default=0.0")
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name= "repair_user", null=True,blank= True, help_text="null= True, blank = true" )

    def __str__(self):
        return "id {}".format(self.id)

class RepairUser(CreateInfoModel):
    REPAIR_STATUS = (
        (1, "PENDING"),
        (2,"COMPLETED"),
        (3,"CANCELED"),
       
    )
    repair_detail= models.ForeignKey(RepairDetail, on_delete=models.PROTECT,related_name='repair_status', help_text="blank = true")
    repair_status = models.PositiveIntegerField(choices = REPAIR_STATUS, default=1,
                                            help_text="where 1=PENDING, 2= COMPLETED, 3=CANCELED")
    comments =  models.CharField(max_length=200, blank= True, help_text= "max length can be upto 200 and blank = true")
    actions_performed =  models.CharField(max_length=200, blank= True, help_text= "max length can be upto 200 and blank = true")

    def __str__(self):
        return "id {}".format(self.id)
 