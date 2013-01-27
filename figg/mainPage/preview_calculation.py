from datetime import date, time, datetime, timedelta
from twitter import data_extract
from common.figgDate import FiggDate

class Regularity:
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

def calculate_preview(current_date, current_time, u_regularity, until):

    regularity = u_regularity.upper()

    # if we calculate the difference between 2 dates, do we get a time delta?
    until_result = data_extract.extract_text(until)
    start_date = data_extract.extract_text(current_date)[0]
    potential_time = data_extract.extract_text(current_time)

    if potential_time:
        start_time = data_extract.extract_text(current_time)[1]
    else:
        start_time = None

    if not until_result:
        if regularity != "NEVER":
            raise "unable to calculate until for %s" % until
        else:
            return [FiggDate(start_date, start_time)]

    until_date, until_time = until_result

    return times_calculation(regularity, start_date, start_time, until_date, until_time)

def times_calculation(regularity, start_date, start_time, until_date, until_time = False):
    if not start_date:
        raise Exception("we need a current date to calculate additional dates from %s" % current_date)

    if start_date > until_date:
        raise "start_date date %s must always be less than until date %s" % (start_date, until_date)

    if regularity == Regularity.HOURLY:
        if not start_time or not until_time:
            raise "we have start time %s and until time %s to calculate hourly rate" % (start_time, until_time)

        return calculate_hourly(start_date, start_time, until_date, until_time)
    else:
        if not start_date or not until_date:
            raise "we need start date %s or until date %s to calculate %s rate" % (regularity, start_date, until_date)

        if regularity == Regularity.DAILY:
            return calculate_daily(start_date, start_time, until_date, until_time)

        if regularity == Regularity.WEEKLY:
            return calculate_weekly(start_date, start_time, until_date, until_time)

        if regularity == Regularity.MONTHLY:
            return calculate_monthly(start_date, start_time, until_date, until_time)
        
        raise Exception("we don't recognise this regularity %s" % regularity)


def calculate_hourly(current_date, current_time, until_date, until_time):

    hours = 0

    if until_date and current_date != until_date:
        hours = (until_date - current_date).days * 24
        
        if hours < 0:
            raise "until date %s is less than current date %s" % (until_date, current_date)
    
    if hours and until_time < current_time:
        raise "until time %s is less than current time %s" % (until_time, current_time)

    hours += (until_time - current_time).seconds / 60
    from_datetime = datetime.combine(current_date, current_time)

    result = []

    for hour in xrange(hours):
        future_event = from_datetime + timedelta(hour)
        result.append(FiggDate(future_event.date, future_event.time))

    return result

def calculate_daily(current_date, current_time, until_date, until_time):

    diff = get_time_diff(current_date, current_time, until_date, until_time)

    result = []

    for day in xrange(diff.days):
        future_date = current_date + timedelta(day)
        result.append(FiggDate(future_date, current_time))

    return result

def get_time_diff(current_date, current_time, until_date, until_time):
    """returns the timedelta between to dates, if no time is added we are inclusive of the last date"""
    if current_time and until_time:
        current_datetime = datetime.combine(current_date, current_time)
        until_datetime = datetime.combine(until_date, until_time)
        return until_datetime - current_date
    else:
        return until_date - current_date + timedelta(1)

def calculate_monthly(current_date, current_time, until_date, until_time):
    current_month = current_date.month
    current_day = current_date.day
    until_month = until_date.month
    until_day = until_date.day

    month_diff = until_month - current_month + 1
    day_diff = until_day - current_day

    if day_diff >= 0:
        month_diff + 1

    result = []

    for month in xrange(month_diff):
        new_month = current_month + month
        new_year = current_date.year

        if new_month > 12:
            new_month = new_month - 12
            new_year = new_year + 1

        result.append(FiggDate(date(new_year, new_month, current_day), current_time))

    return result

def calculate_weekly(current_date, current_time, until_date, until_time):
    diff = get_time_diff(current_date, current_time, until_date, until_time)
    week_diff = diff.days/7 + 1

    result = []

    for week in xrange(week_diff):
        result.append(FiggDate(current_date + timedelta(week * 7), current_time))

    return result




