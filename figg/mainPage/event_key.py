import random

NONE = "none"
DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"

def create_date_key(event_date, event_time = False):
    """ a unique string for an event date/time for sorting maintaining order in pagination """
    date_string = event_date.strftime("%Y%m%d")
    if event_time:
        minutes = str(event_time.minute + 1)

        if len(minutes) == 1:
            minutes = "0%s" % minutes

        hours = event_time.strftime("%H")
        time_string = "%s%s" % (hours, minutes)
    else:
        time_string = "0000"

    rnd = str(random.randint(0, 999999))
    
    while len(rnd) < 6:
        rnd = "0%s" % rnd

    return long(date_string + time_string + rnd)

def date_key(event_date):
    date_string = event_date.strftime("%Y%m%d")
    return long("%s0000000000" % date_string)
