from common import validation
from common.validation import safe_get
from django.utils.html import escape
from twitter import data_extract
from mainPage import venue_calculation
from django.utils.html import strip_tags
from common.user_tag import UserTag
from datetime import datetime
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def process_json_args(cal_type, cal, tag, string_post_date, string_last_date, string_last_time):
    args = {}
    if cal_type:
        args["cal_type"] = cal_type.strip()

    if cal:
        args["user"] = cal.strip()
    
    if tag:
        args["tag"] = tag.strip().lstrip('#')
    user_tag = UserTag(**args)
    post_date = datetime.strptime(string_post_date, "%Y%m%d")

    if string_last_date and string_last_date != "null":
        last_date = datetime.strptime(string_last_date, "%Y%m%d")
    else:
        last_date = False

    return (user_tag, post_date, last_date)

def extract_event_args(request, require_id = False):
    '''event validation library to pull out the event args for event creator and
    event editor'''

    event = {}
    event["errors"] = []
    description = strip_tags(request.POST.get("description"))
    if len(description):
        event["description"] = description
    else:
        event["description"] = None

    event["title"] = safe_get(request.POST, "title")
    event["user"] = request.user
    possible_date = safe_get(request.POST, ('eventDate'))
    possible_time = safe_get(request.POST, 'eventTime')
    possible_venue = safe_get(request.POST, 'venue')
    event["invited"] = set(escape(x) for x in request.POST.getlist('who[]'))
    event["public"] = request.POST.get('public') == "true"
    repeat_regularity = safe_get(request.POST, "repeatEvent")
    repeat_until = safe_get(request.POST, 'repeatUntil')

    if repeat_regularity:
        event["repeat_regularity"]= repeat_regularity

    if repeat_until:
        event["repeat_until"] = repeat_until

    if require_id:
        event["event_id"] = safe_get(request.POST, "event_id")

        if event["event_id"] == None:
            logger.error("unable to find an event id for %s" % request.POST.items())
            event["errors"].append("event_id")

    if not event["title"]:
        event["errors"].append("title")

    if len(event["title"]) > 100:
        logger.error("title is too long for %s" % request.POST.items())
        event["errors"].append("title")

    if event["description"] and len(event["description"]) > 250:
        logger.error("description is too long for %s" % request.POST.items())
        event["errors"].append("description")

    if possible_date and possible_date != "null":
        logger.info("we are extracting date, with %s" % possible_date)
        event["event_date"] = data_extract.extract_text(possible_date, today = None)[0]
        logger.info("done extracting with %s" % event["event_date"]);
    else:
        event["errors"].append("event_date")

    if possible_time and possible_time != "null":
        logger.info("we are extracting time with %s" % possible_time)
        event["event_time"] = data_extract.get_time(possible_time)
        logger.info("done extracting with %s" % event["event_time"]);

        if not ["event_time"]:
            event["errors"].append("event_time")
            event["event_time"] = possible_time

    if possible_venue and possible_venue != 'null':
        try:
            try:
                venue_id = int(possible_venue)
                event["event_venue"] = venue_calculation.get_venue_from_id(venue_id)
            except:
                event["event_venue"] = venue_calculation.get_venue_from_name(possible_venue)
        except:
            logger.error("unable to find a venue with %s" % possible_venue)
            event["errors"].append("venue")

    return event

def get_date(potential_date):
    try:
        cast_date = datetime.strptime(potential_date, '%d%b%Y').date()
    except:
        cast_date = datetime.strptime(potential_date, '%Y%m%d').date()

    return cast_date

def get_query_args(request):
    if not request.method == "GET":
        raise ValidationException("wrong request method used")

    args = {}
    start_date = safe_get(request.GET, "startDate")

    if start_date:
        args["start_date"] = get_date(start_date)

    end_date = safe_get(request.GET, "endDate")

    if end_date:
        args["end_date"] = get_date(end_date)

    direction = safe_get(request.GET, "direction")

    if direction: 
        args["up"] = direction == "bottom"

    args["start_key"] = safe_get(request.GET, "startKey")
    args["end_key"] = safe_get(request.GET, "endKey")

    if request.user.is_authenticated():
        args["user"] = request.user
    else:
        args["user"] = False

    if not (start_date or end_date or args["start_key"] or args["end_key"]):
        raise ValidationException("flawed args %s" % args)

    return args

def error_check(event):
    if "event_date" in event["errors"]:
        logger.error("we're missing an event date for %s %s" % (event["description"], event["username"]))
        return HttpResponse(encoder.encode("we can't recognise that date, try e.g. 13Jul12"), mimetype='application/json') 

    if "event_time" in event["errors"]:
        logger.error("we're can't understand the time %s for %s %s" % (event["time"], event["description"], event["username"]))
        return HttpResponse(encoder.encode("we can't recognise that time, try e.g. 11:00 pm"), mimetype='application/json') 

    if "title" in event["errors"]:
        logger.error("we're missing a title for %s %s" % (event["event_date"], event["username"]))
        return HttpResponse(encoder.encode("please add a name for your event"), mimetype='application/json')

class ValidationException(Exception):
    pass
