from django.shortcuts import render
from django.dispatch import receiver
from src.custom_lib.functions.date_converter import ad_to_bs_converter
from simple_history.signals import (pre_create_historical_record, post_create_historical_record)
from src.item.models import ItemCategory
# from simple_history.
# Create your views here.

@receiver(pre_create_historical_record)
def pre_create_historical_record_callback(sender, **kwargs):
    print("signal is running")
    history_instance = kwargs['history_instance']
    date_ad = history_instance.history_date
    date_bs = ad_to_bs_converter(date_ad)
    history_instance.history_date_bs = date_bs



# receiver(post_create_historical_record)
# def post_create_funcation(sender, **kwargs):
#     print("post save called")