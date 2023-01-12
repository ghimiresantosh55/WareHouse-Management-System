# import time
import datetime
from datetime import timedelta

# third-party
import nepali_datetime
from django.utils import timezone


# Input Date Format Should be (YYYY-MM-DD)
def get_fiscal_year(date_in_string):
    fiscal_calc = {}
    # date_in_string = "2021-02-17"
    li_ad = list(date_in_string.split("-"))
    year = int(li_ad[0])
    month = int(li_ad[1])
    day = int(li_ad[2])
    curr_date_ad_obj = datetime.date(year, month, day)
    curr_date_bs = nepali_datetime.date.from_datetime_date(curr_date_ad_obj)
    curr_date_bs = str(curr_date_bs)

    li_bs = list(curr_date_bs.split("-"))

    # adding of two list
    li = li_ad + li_bs
    #
    # for nepali fiscal year
    if int(li[4]) <= 3:
        if int(li[5]) <= 32:
            # for end of fiscal year
            fiscal_year_end_bs = int(li[3])

            # converting into string
            fiscal_year_end_bs = str(fiscal_year_end_bs)
            end_string_bs = fiscal_year_end_bs

            # storing the integer into list
            end_map_bs = map(int, end_string_bs)
            fiscal_year_short_end_bs = list(end_map_bs)
            # concatinating last two objects in list 2077 to 77
            # fiscal_year_short_end_bs = [2,0,7,7]
            fiscal_year_short_end_bs = str(fiscal_year_short_end_bs[2]) + str(fiscal_year_short_end_bs[3])

            fiscal_year_start_bs = int(li[3]) - 1
            fiscal_year_start_bs = str(fiscal_year_start_bs)
            start_string_bs = fiscal_year_start_bs
            start_map_bs = map(int, start_string_bs)
            fiscal_year_short_start_bs = list(start_map_bs)
            fiscal_year_short_start_bs = str(fiscal_year_short_start_bs[2]) + str(fiscal_year_short_start_bs[3])

            # for storing full date
            fiscal_year_full_start_date_bs = fiscal_year_start_bs + str('-04-01')
            str_temp1_bs = int(fiscal_year_start_bs)
            # converting into date

            if (str(fiscal_year_end_bs) == "2001" or str(fiscal_year_end_bs) == "2002" or str(
                    fiscal_year_end_bs) == "2005" or
                    str(fiscal_year_end_bs) == "2006" or str(fiscal_year_end_bs) == "2008" or str(
                        fiscal_year_end_bs) == "2010" or
                    str(fiscal_year_end_bs) == "2013" or str(fiscal_year_end_bs) == "2014" or str(
                        fiscal_year_end_bs) == "2017" or
                    str(fiscal_year_end_bs) == "2021" or str(fiscal_year_end_bs) == "2025" or str(
                        fiscal_year_end_bs) == "2028" or
                    str(fiscal_year_end_bs) == "2029" or str(fiscal_year_end_bs) == "2032" or str(
                        fiscal_year_end_bs) == "2033" or
                    str(fiscal_year_end_bs) == "2036" or str(fiscal_year_end_bs) == "2037" or str(
                        fiscal_year_end_bs) == "2040" or
                    str(fiscal_year_end_bs) == "2041" or str(fiscal_year_end_bs) == "2044" or str(
                        fiscal_year_end_bs) == "2048" or
                    str(fiscal_year_end_bs) == "2052" or str(fiscal_year_end_bs) == "2055" or str(
                        fiscal_year_end_bs) == "2056" or
                    str(fiscal_year_end_bs) == "2058" or str(fiscal_year_end_bs) == "2060" or str(
                        fiscal_year_end_bs) == "2063" or
                    str(fiscal_year_end_bs) == "2064" or str(fiscal_year_end_bs) == "2067" or str(
                        fiscal_year_end_bs) == "2068" or
                    str(fiscal_year_end_bs) == "2071" or str(fiscal_year_end_bs) == "2075" or str(
                        fiscal_year_end_bs) == "2079" or
                    str(fiscal_year_end_bs) == "2082" or str(fiscal_year_end_bs) == "2083" or str(
                        fiscal_year_end_bs) == "2084" or
                    str(fiscal_year_end_bs) == "2087" or str(fiscal_year_end_bs) == "2088" or str(
                        fiscal_year_end_bs) == "2091" or
                    str(fiscal_year_end_bs) == "2092" or str(fiscal_year_end_bs) == "2094" or str(
                        fiscal_year_end_bs) == "2095" or
                    str(fiscal_year_end_bs) == "2096" or str(fiscal_year_end_bs) == "2098"):

                fiscal_year_full_end_date_bs = fiscal_year_end_bs + str('-03-32')

            else:
                fiscal_year_full_end_date_bs = fiscal_year_end_bs + str('-03-31')
            # converting into string
            fiscal_year_full_end_date_bs = str(fiscal_year_full_end_date_bs)
            short_fiscal_session_bs = fiscal_year_short_start_bs + '/' + fiscal_year_short_end_bs
        else:
            return 0

    else:
        fiscal_year_end_bs = int(li[3])
        fiscal_year_end_bs = str(fiscal_year_end_bs)
        temp1_bs = fiscal_year_end_bs
        end_string_bs = fiscal_year_end_bs
        end_map_bs = map(int, end_string_bs)
        fiscal_year_short_end_bs = list(end_map_bs)
        fiscal_year_short_end_bs = str(fiscal_year_short_end_bs[2]) + str(fiscal_year_short_end_bs[3])
        temp3_bs = fiscal_year_short_end_bs
        fiscal_year_start_bs = int(li[3]) + 1
        fiscal_year_start_bs = str(fiscal_year_start_bs)
        temp2_bs = fiscal_year_start_bs
        start_string_bs = fiscal_year_start_bs
        start_map_bs = map(int, start_string_bs)
        fiscal_year_short_start_bs = list(start_map_bs)
        fiscal_year_short_start_bs = str(fiscal_year_short_start_bs[2]) + str(fiscal_year_short_start_bs[3])
        temp4_bs = fiscal_year_short_start_bs
        fiscal_year_full_start_date_bs = temp1_bs + str('-04-01')
        str_temp1_bs = int(fiscal_year_start_bs)
        # converting into date
        fiscal_year_full_end_date_bs = nepali_datetime.date(str_temp1_bs, 4, 1)
        # for fiscal year full date
        fiscal_year_full_end_date_bs = fiscal_year_full_end_date_bs - timedelta(days=1)
        # converting into string
        fiscal_year_full_end_date_bs = str(fiscal_year_full_end_date_bs)
        fiscal_year_start_bs = temp1_bs
        fiscal_year_end_bs = temp2_bs
        fiscal_year_short_start_bs = temp3_bs
        fiscal_year_short_end_bs = temp4_bs
        short_fiscal_session_bs = fiscal_year_short_start_bs + '/' + fiscal_year_short_end_bs

    # for english fiscal year
    if int(li[1]) <= 3:
        if int(li[2]) < 32:

            # for end of fiscal year
            fiscal_year_end_ad = int(li[0])

            # converting into string
            fiscal_year_end_ad = str(fiscal_year_end_ad)
            end_string = fiscal_year_end_ad

            # storing the integer into list
            end_map = map(int, end_string)
            fiscal_year_short_end_ad = list(end_map)
            # concatinating last two objects in list 2020 to 20
            fiscal_year_short_end_ad = str(fiscal_year_short_end_ad[2]) + str(fiscal_year_short_end_ad[3])

            fiscal_year_start_ad = int(li[0]) - 1
            fiscal_year_start_ad = str(fiscal_year_start_ad)
            start_string = fiscal_year_start_ad
            start_map = map(int, start_string)
            fiscal_year_short_start_ad = list(start_map)
            fiscal_year_short_start_ad = str(fiscal_year_short_start_ad[2]) + str(fiscal_year_short_start_ad[3])

            # for storing full date
            fiscal_year_full_start_date_ad = fiscal_year_start_ad + str('-04-01')
            fiscal_year_full_end_date_ad = fiscal_year_end_ad + str('-03-31')
            short_fiscal_session_ad = fiscal_year_short_start_ad + '/' + fiscal_year_short_end_ad
            full_fiscal_session_ad = fiscal_year_start_ad + '/' + fiscal_year_end_ad
            full_fiscal_session_bs = fiscal_year_start_bs + '/' + fiscal_year_end_bs
            fiscal_calc = {
                "current_date_ad": date_in_string,
                "fiscal_year_full_start_date_ad": fiscal_year_full_start_date_ad,
                "fiscal_year_full_end_date_ad": fiscal_year_full_end_date_ad,
                "fiscal_year_start_ad": fiscal_year_start_ad,
                "fiscal_year_end_ad": fiscal_year_end_ad,
                "fiscal_year_short_start_ad": fiscal_year_short_start_ad,
                "fiscal_year_short_end_ad": fiscal_year_short_end_ad,
                "short_fiscal_session_ad": short_fiscal_session_ad,
                "curr_date_bs": curr_date_bs,
                "fiscal_year_full_start_date_bs": fiscal_year_full_start_date_bs,
                "fiscal_year_full_end_date_bs": fiscal_year_full_end_date_bs,
                "fiscal_year_start_bs": fiscal_year_start_bs,
                "fiscal_year_end_bs": fiscal_year_end_bs,
                "fiscal_year_short_start_bs": fiscal_year_short_start_bs,
                "fiscal_year_short_end_bs": fiscal_year_short_end_bs,
                "short_fiscal_session_bs": short_fiscal_session_bs,
                "full_fiscal_session_ad": full_fiscal_session_ad,
                "full_fiscal_session_bs": full_fiscal_session_bs
            }
        else:
            return 0

    else:
        fiscal_year_end_ad = int(li[0])
        fiscal_year_end_ad = str(fiscal_year_end_ad)
        temp1 = fiscal_year_end_ad
        end_string = fiscal_year_end_ad
        end_map = map(int, end_string)
        fiscal_year_short_end_ad = list(end_map)
        fiscal_year_short_end_ad = str(fiscal_year_short_end_ad[2]) + str(fiscal_year_short_end_ad[3])
        temp3 = fiscal_year_short_end_ad
        fiscal_year_start_ad = int(li[0]) + 1
        fiscal_year_start_ad = str(fiscal_year_start_ad)
        temp2 = fiscal_year_start_ad
        start_string = fiscal_year_start_ad
        start_map = map(int, start_string)
        fiscal_year_short_start_ad = list(start_map)
        fiscal_year_short_start_ad = str(fiscal_year_short_start_ad[2]) + str(fiscal_year_short_start_ad[3])
        temp4 = fiscal_year_short_start_ad
        # reversing the start and end date.
        fiscal_year_full_start_date_ad = temp1 + str('-04-01')
        fiscal_year_full_end_date_ad = temp2 + str('-03-31')
        fiscal_year_start_ad = temp1
        fiscal_year_end_ad = temp2
        fiscal_year_short_start_ad = temp3
        fiscal_year_short_end_ad = temp4
        short_fiscal_session_ad = fiscal_year_short_start_ad + '/' + fiscal_year_short_end_ad
        full_fiscal_session_ad = fiscal_year_start_ad + '/' + fiscal_year_end_ad
        full_fiscal_session_bs = fiscal_year_start_bs + '/' + fiscal_year_end_bs
        fiscal_calc = {
            "current_date_ad": date_in_string,
            "fiscal_year_full_start_date_ad": fiscal_year_full_start_date_ad,
            "fiscal_year_full_end_date_ad": fiscal_year_full_end_date_ad,
            "fiscal_year_start_ad": fiscal_year_start_ad,
            "fiscal_year_end_ad": fiscal_year_end_ad,
            "fiscal_year_short_start_ad": fiscal_year_short_start_ad,
            "fiscal_year_short_end_ad": fiscal_year_short_end_ad,
            "short_fiscal_session_ad": short_fiscal_session_ad,
            "curr_date_bs": curr_date_bs,
            "fiscal_year_full_start_date_bs": fiscal_year_full_start_date_bs,
            "fiscal_year_full_end_date_bs": fiscal_year_full_end_date_bs,
            "fiscal_year_start_bs": fiscal_year_start_bs,
            "fiscal_year_end_bs": fiscal_year_end_bs,
            "fiscal_year_short_start_bs": fiscal_year_short_start_bs,
            "fiscal_year_short_end_bs": fiscal_year_short_end_bs,
            "short_fiscal_session_bs": short_fiscal_session_bs,
            "full_fiscal_session_ad": full_fiscal_session_ad,
            "full_fiscal_session_bs": full_fiscal_session_bs
        }
    return fiscal_calc


def get_fiscal_year_code_bs():
    fiscal_year_code = get_fiscal_year(str(timezone.now().date()))['short_fiscal_session_bs']
    return fiscal_year_code


def get_fiscal_year_code_ad():
    fiscal_year_code_ad = get_fiscal_year(str(timezone.now().date()))['short_fiscal_session_ad']
    return fiscal_year_code_ad


def get_full_fiscal_year_code_ad():
    full_fiscal_year_code_ad = get_fiscal_year(str(timezone.now().date()))['full_fiscal_session_ad']
    return full_fiscal_year_code_ad


def get_full_fiscal_year_code_bs():
    full_fiscal_year_code_bs = get_fiscal_year(str(timezone.now().date()))['full_fiscal_session_bs']
    return full_fiscal_year_code_bs
