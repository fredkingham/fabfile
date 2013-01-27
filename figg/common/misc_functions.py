from datetime import datetime, date

def hash_id(event_id):
    return event_id

def decode_id(event_id):
    return event_id

def split_event_ids(event_id):
    if "!" not in event_id:
        raise "incorrectly formed event_id %s" % event_id

    split_event_id = event_id.split("!")
    parent_event_id = split_event_id[0]
    event_time_id = split_event_id[1]

    return (int(parent_event_id), int(event_time_id))

def combine_event_ids(event_id, event_time_id):
    return "%s!%s" % (event_id, event_time_id)

def generic_date_display(some_date):
    return some_date.strftime("%a %d %B %Y")

def generic_datetime_display(some_datetime):
    return some_datetime.strftime("%a %d %B %Y %H:%M")

def generic_time_display(some_time):
    return some_time.strftime("%H:%M")

def generic_figg_date_display(some_figg_date):
    return generic_date_time_display(some_figg_date.date, some_figg_date.time)

def generic_date_time_display(some_date, some_time):
    new_date = generic_date_display(some_date)

    if some_time:
        return "%s %s" % (new_date, generic_time_display(some_time))
    else:
        return new_date

