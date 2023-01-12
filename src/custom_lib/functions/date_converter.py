import datetime
import nepali_datetime


def ad_to_bs_converter(ad_obj):
    date_ad = ad_obj
    year_ad = date_ad.year
    month_ad = date_ad.month
    day_ad = date_ad.day
    date_ad_obj = datetime.date(year_ad, month_ad, day_ad)
    date_bs = nepali_datetime.date.from_datetime_date(date_ad_obj)
    return date_bs


def bs_to_ad_converter(bs_obj):
    pass
