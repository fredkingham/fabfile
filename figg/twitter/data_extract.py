import re 
import calendar
from datetime import date, timedelta, datetime, time
from common import email_me
from django.conf import settings
from django.contrib.auth.models import User
from dateutil import parser

# doesn't include MAY at this time, that's gonna get complicated
MONTH_NAMES = {
        "JANUARY": "JAN",
        "FEBRUARY": "FEB",
        "MARCH": "MAR",
        "APRIL": "APR",
        "JUNE": "JUN",
        "JULY": "JUL",
        "AUGUST": "AUG",
        "SEPTEMBER": "SEP",
        "OCTOBER": "OCT",
        "NOVEMBER": "NOV",
        "DECEMBER": "DEC"
        }

MONTH_NUMBERS = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
        } 

# we use an internal representation of the days as the 3 digit day name as
# defined by the strp time function
DAY_NAMES = {
        "MONDAY": "MON",
        "TUESDAY": "TUE",
        "TUES": "TUE",
        "WEDNESDAY": "WED",
        "THURSDAY": "THU",
        "THURS": "THU",
        "FRIDAY": "FRI"
        }

DAY_NUMBERS = {
        "SUN": 1,
        "MON": 2,
        "TUE": 3,
        "WED": 4,
        "THU": 5,
        "FRI": 6,
        "SAT": 7,
        }

def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month / 12
    month = month % 12 + 1
    day = min(source_date.day,calendar.monthrange(year,month)[1])
    return date(year,month,day)

def get_date_on(upper):
    regex = r"(?:\W|\Z)ON (?:THE )?(\d\d?)(?:ST|ND|RD|TH)?(?:\W|\Z)"
    results = re.findall(regex, upper)

    if len(results):
        count = 0
        for result in results:
            ignore_regex = r"%s(ST|ND|RD|TH) (STREET|ST|AVENUE|AVE|BLOCK|FLOOR)" % result
            invalid = re.search(ignore_regex, upper)

            if not invalid:
                clean = upper.replace("ON %s" % result, "")
                clean = clean.replace("ON THE %s" % result, "")
                return (int(result), clean)

            count += 1


def get_month(upper):
    month_types = MONTH_NAMES.keys() + MONTH_NAMES.values()

    months_exist = filter(lambda x: x in upper, month_types) 

    for month_exists in months_exist:
        regex1 = r"[^A-Z](%s)[^A-Z]" % month_exists
        regex2 = r"[^A-Z](%s)$" % month_exists
        regex3 = r"^(%s)[^A-Z]" % month_exists

        for regex in [regex1, regex2, regex3]:
            search_result = re.search(regex, upper)

            if search_result:
                found_month = search_result.group(1)

                if found_month in MONTH_NAMES.values(): 
                    return MONTH_NUMBERS[found_month]
                else:
                    return MONTH_NUMBERS[MONTH_NAMES[found_month]]

def get_time(upper, with_match = False):
    upper = upper.upper()
    result = time_with_colon(upper, with_match)

    if not result:
        result = get_time_with_ampm(upper, with_match)

    if not result:
        result = time_with_colon(upper, with_match)

    if not result:
        result = get_time_at(upper, with_match)

    return result

def time_with_colon(upper, with_match):
    regex = r"(?:\A|\s)((\d\d?):(\d\d)(?:\W)?(PM)?(?:\W|\Z))"
    search_result = re.search(regex, upper)

    if search_result:
        if int(search_result.groups()[1]) > 24:
            return None

        if search_result:
            results = search_result.groups()

            hours = int(results[1])
            minutes =  int(results[2])

            if len(results) == 4 and results[3] == "PM" and hours < 12:
                hours = hours + 12

            if with_match:
                return(time(hours, minutes), search_result.groups()[0])
            else:
                return time(hours, minutes)

def get_time_with_ampm(upper, with_match):
    regex = r"((?:\A|\s)(\d\d?)(?:\W)?(PM|AM)(?:\W|\Z))"

    search_result = re.search(regex, upper)

    if search_result:
        hour = int(search_result.groups()[1])

        if search_result.groups()[2] == "PM":
            hour = hour + 12
        
        if hour > 23:
            return None 

        if with_match:
            return (time(hour, 0), search_result.groups()[0].strip())
        else:
            return time(hour, 0)

def get_time_at(upper, with_match):
    regex = r"(?:\A|\W)(AT (\d\d))(?:\W|\Z)"
    search_result = re.search(regex, upper)
    if search_result:
        result = int(search_result.groups()[1])
        return (time(result), search_result.groups()[0])

def get_day_number(upper):

    regex1 = r"\W(\d\d?)(ST|ND|RD|TH)(?:\W|\Z)?"
    regex2 = r"\W(\d\d?)(?:\W|\Z)?"

    for regex in [regex1, regex2]:
        search_result = re.search(regex, upper)

        if search_result:
            all_returned = search_result.groups()

            day = int(all_returned[0]) 

            if day > 31:
                print "the date seems to be greater than 31...."
                return

            return day

def get_from_iso(upper):
    if len(upper.strip()):
        try:
            return parser.parse(upper)
        except:
            return

def get_default_date(upper):
    regex = r"(\d{1,2})(?:\W?)([a-zA-Z]{3,})(?:\W?)(\d{2,4}?)(?:\W|\Z)"
    search_result = re.search(regex, upper)

    if search_result:
        day, month_name, year = search_result.groups()
        if month_name in MONTH_NAMES.values():
            month = datetime.strptime(month_name, "%b").month
        elif month_name in MONTH_NAMES:
            month = datetime.strptime(month_name, "%B").month
        else:
            return

        return date(calc_year(int(year)), month, int(day))

def get_sequence(upper, today):

    if "TODAY" in upper:
        return today

    if "TOMORROW" in upper:
        tomorrow = timedelta(1)
        return today + tomorrow

# we use day numbers keys because they are unique
    all_days = DAY_NAMES.keys() + DAY_NUMBERS.keys()
    days = filter(lambda x: x in upper, all_days)

    if len(days) > 0:
       found_day = days[0] 
       next_day = "NEXT %s" % found_day
       next_week_on = "NEXT WEEK ON %s" % found_day
       next_week = next_day in upper or next_week_on in upper
       return today + get_time_delta(found_day, today, next_week) 

def get_time_delta(future_day, today, next_week = False):

    if future_day not in DAY_NUMBERS:
        day_num = DAY_NUMBERS[DAY_NAMES[future_day]]
    else:
        day_num = DAY_NUMBERS[future_day]

    today_name = today.strftime("%a").upper()
    today_num = DAY_NUMBERS[today_name]
    if today_num < day_num and not next_week:
        return timedelta(day_num - today_num)
    else:
        return timedelta(day_num - today_num + 7)

# we should make sure that there is a space in front of the year 
# or if there is no space, check to see if its a month in front
def get_year(upper):
    regex = "(\d\d\d\d)"
    search_result = re.search(regex, upper)
    if search_result:
        potential_year = search_result.groups()[0]
        if potential_year > 1900:
            return potential_year

def calc_year(upper):
    if len(str(upper)) == 4:
        return upper
    
    if len(str(upper)) != 2:
        raise DateException("incorrect year with %s" % upper)

    return upper + 2000

def extract_text_decorator(function):
    def email_results(*args, **kwargs):
        results = function(*args, **kwargs)
        if not settings.DEBUG:
            subject = "results from a tweet date"
            if results:
                message = "there text was \n\n%s\n\n we think it means \n %s %s" % (args, results[0], results[1])
            else:
                message = "in text %s we were unable to find a date" % args
            email_me.send(subject, message)
        return results

    return email_results

# we need to add a relative date as well as an event date
def extract_text(text, today = date.today(), relative_date = date.today()):
    if text:
        invited = get_invited_tags(text, "@")

        for invites in invited:
            with_at = "@%s" % invites
            text.replace(with_at, "")

        upper = text.upper()

        time_tuple = get_time(upper, with_match = True)

        if time_tuple:
            upper = upper.replace(time_tuple[1], "")
            time = time_tuple[0]
        else:
            time = None

        iso_date = get_from_iso(upper)

        if iso_date:
            return (iso_date.date(), iso_date.time())

        default_date = get_default_date(upper)

        if default_date:
            return (default_date, time)

        date_on = get_date_on(upper)

        if date_on:
            day = date_on[0]
            upper = date_on[1]
        else:
            day = False
        
        month = get_month(upper)

        if not day:
            day = get_day_number(upper)

        year = get_year(upper)

        if not year:
            if month:
                if month < today.month:
                    year = today.year + 1
                elif month == today.month and day and day < today.day:
                    year = today.year + 1
                else:
                    year = today.year

        if day and month:
            return (date(int(year), int(month), int(day)), time)

        sequence_date = get_sequence(upper, today)

        if sequence_date:
            return (sequence_date, time)

        if day:
            if today.day > day:
                new_date = date(today.year, today.month, day)
                next_month = add_months(new_date, 1)
                return (next_month, time)
            else:
                no_given_month = today.month
                return (date(today.year, today.month, day), time)

        if time:
            return (today, time)

def get_invited(tweet):
    results =  get_invited_tags(tweet, "@")
    if results:
        users = User.objects.filter(username__in = list(results)).values_list("username", flat = True)
        return users
    else:
        return []

def get_tags(tweet):
    return get_invited_tags(tweet, "#")

# pulls out the specially prefexed charecters @invite #tag
def get_invited_tags(tweet, special):
    if tweet:
        regex = r"(?:\s|\A)%s(\w*)" % special
        results = re.findall(regex, tweet)
        return results

    return list()

class DateException(Exception):
    pass
