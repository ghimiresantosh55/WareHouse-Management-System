from django.db import models
# Create your models here.
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from simple_history.signals import pre_create_historical_record
from src.custom_lib.functions.date_converter import ad_to_bs_converter


# do not import any models here, it can raise circular import problem
@receiver(pre_create_historical_record)
def pre_create_historical_record_callback(sender, **kwargs):
    history_type = kwargs['history_instance'].history_type
    history_instance = kwargs['history_instance']
    # history_type = "s"
    if history_type == "+":
        date_ad = kwargs['instance'].created_date_ad
        date_bs = kwargs['instance'].created_date_bs
        history_instance.history_date = date_ad
        history_instance.history_date_bs = date_bs
    elif history_type == "~" or history_type == "-":
        date_ad = kwargs['history_instance'].history_date
        date_bs = ad_to_bs_converter(date_ad)
        history_instance.history_date_bs = date_bs
    else:
        raise ValueError({f'history_type in Log table {sender} did not match symbols: +(add), ~(update), -(delete)'})



class LogBase(models.Model):
    history_date_bs = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        abstract = True


class UserAccessLog(models.Model):
    ACCESS_TYPE = (
        (1, "LOGIN"),
        (2, "LOGOUT")
    )
    user_id = models.PositiveIntegerField()
    access_type = models.PositiveIntegerField(choices=ACCESS_TYPE, help_text="1-LOGIN, 2-LOGOUT")
    access_date_ad = models.DateTimeField(blank=True, null=True)
    access_date_bs = models.CharField(max_length=10,  blank=True, null=True)
    ipv4_address = models.CharField(max_length=15, blank=True) # 192.168.111.111
    ipv6_address = models.CharField(max_length=39, blank=True) # 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    access_location = models.CharField(max_length=100, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    browser_version = models.CharField(max_length=50, blank=True)
    platform = models.CharField(max_length=50, blank=True)
    mobile = models.BooleanField(blank=True, null=True)
    robot = models.BooleanField(blank=True, null=True)
    access_coordinate_la = models.CharField(max_length=10, blank=True)
    access_coordinate_lo = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.access_date_ad = timezone.now()
            self.access_date_bs = ad_to_bs_converter(self.access_date_ad)
        super().save(*args, **kwargs)


