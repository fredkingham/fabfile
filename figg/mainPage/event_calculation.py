from mainPage.models import AttendingStatus, Event, Venue, EventImage
from django.db.models import Q
from datetime import datetime
from collections import defaultdict
from django.contrib.auth.models import User
from twitter import user_calculation
from mainPage import note_calculation, event_key
import os
from notifications import queue_writer
from common import misc_functions
from mainPage.event_option import EventOption
from mainPage.event_holder import EventHolderForUser, SearchHolder, SpecificEventHolder, SeriesEventHolder
from twitter import BIGGER
import logging
logger = logging.getLogger(__name__)


def get_event_count(user):
    return AttendingStatus.objects.filter(status=AttendingStatus.CREATOR, user=user).filter(event__deleted=False).count()


def get_dateline(user, start_date, end_date):
    '''returns a map of dates to a count of events, dates will always be for a
    month'''

    event_dates = Event.objects.filter(attending_status__user=user)
    event_dates = event_dates.filter(deleted=False)
    event_dates = event_dates.filter(date__gte=start_date, date__lt=end_date)
    event_dates = event_dates.filter(attending_status__status__in=[AttendingStatus.ACCEPTED, AttendingStatus.ADDED])
    event_dates = event_dates.distinct()
    event_dates = event_dates.values("date", "id")

    #query isn't aggregating at the moment probably because of time being specified
    #in the meta field, so we can just count it all up.
    date_to_event = defaultdict(set)

    for event_date in event_dates:
        date_to_event[event_date["date"]].add(event_date["id"])

    date_to_count = {}
    for date_key in date_to_event:
        date_to_count[date_key.isoformat()] = len(date_to_event[date_key])

    return date_to_count


def calculate_stream(start_date=False, end_date=False, start_key=False, end_key=False, user=False, up=True):
    ''' returns an ordered list of event structs for json translation for the stream '''
    event_holder = EventHolderForUser(
        start_date, end_date, user=user, start_key=start_key, end_key=end_key)
    event_holder.populate()
    return event_holder


def calculate_specific(start_date=False, end_date=False, start_key=False, end_key=False, user=False, cal=False, tag=False):
    """ returns an event holder for the specific series """
    event_holder = SpecificEventHolder(**locals())
    event_holder.populate()
    return event_holder


def calculate_series(series, start_date=False, end_date=False, start_key=False, end_key=False, user=False):
    """ returns a specific list for the cal or tag """
    event_holder = SeriesEventHolder(**locals())
    event_holder.populate()
    return event_holder


def get_search_events(search_term, start_date=False, end_date=False, start_key=False, end_key=False, user=False):
    event_holder = SearchHolder(**locals())
    event_holder.populate()
    return event_holder


def format_venue(venue):

    if venue:
        last_bracket = venue.rfind("(")
        venue_name = venue[:last_bracket].strip()
        venue_code = venue[last_bracket + 1:].strip(")").strip()
        # venue is passed in with the form [name],[postcode]
        venue = Venue.objects.get(name=venue_name, postcode=venue_code)
    else:
        venue = None

    return venue


def get_img_for_event(user):
    root = user_calculation.get_imgs([user.username], BIGGER)[user.username]
    return os.path.basename(root)


def process_img(img):
    img_obj = EventImage(img=img)
    img_obj.save()
    return img_obj


def cancel_event(event_id, user):
    count = AttendingStatus.objects.filter(
        event__id=event_id, user=user, status=AttendingStatus.CREATOR).count()
    if not count:
        logger.error("unexpected user %s trying to cancel %s" % (
            user.username, event_id))
        return False
    else:
        event = Event.objects.get(id=event_id)
        event.deleted = True
        event.save()
        AttendingStatus.objects.filter(event__id=event_id, user=user).exclude(
            status=AttendingStatus.CREATOR).update(deleted=True)
        attending_status = AttendingStatus.objects.get(
            event__id=event_id, user=user, status=AttendingStatus.CREATOR)
        added = AttendingStatus.objects.filter(event__id=event_id)
        added = added.filter(Q(status=AttendingStatus.ADDED) | Q(
            status=AttendingStatus.ACCEPTED))
        added = added.exclude(user=user)

        for i in added:
            queue_writer.add_cancel(i.user, attending_status)

        return True


def edit_event(event, event_date, title, description, user, event_time=None, event_venue=None, public=False, invited=[]):
    count = AttendingStatus.objects.filter(
        event=event, user=user, status=AttendingStatus.CREATOR).count()

    if not count:
        logger.error("unexpected user %s trying to edit %s" % (
            user.username, event))
        return False

    event_changed = False

    if title != event.title:
        event_changed = True
        event.title = title

    if (description or event.description) and (description != event.description):
        event_changed = True
        event.description = description

    if public != event.public:
        event_changed = True
        event.public = public

    if event_time != event.time:
        event_changed = True
        event.time = event_time

    if event_date != event.date:
        event_changed = True
        event.date = event_date

    if event.venue and not event_venue:
        event_changed = True
        event.venue = None
    elif event_venue:
        venue = format_venue(event_venue)
        if venue != event.venue:
            event_changed = True
            event.venue = venue

    if event_changed:
        print "event date %s, event_time %s" % (event.date, event.time)
        event.key = event_key.create_date_key(event.date, event.time)
        event.save()

    if invited:
        note_calculation.invite(user, invited, event)

    return True


def get_event_img_from_id(event_time_id):
    username = AttendingStatus.objects.filter(event_time__id=event_time_id, status=AttendingStatus.CREATOR).distinct()[0].user.username
    img = user_calculation.get_imgs([username], BIGGER)[username]
    return img


def unable(statuses):
    for invited in statuses:
        invited.status = AttendingStatus.UNABLE
        invited.save()


def accept(user, action, event_dbo):
    public = action == EventOption.ACCEPT
    statuses = AttendingStatus.objects.filter(
        event=event_dbo, user=user, status=AttendingStatus.INVITED)
    from_status_users = AttendingStatus.objects.filter(to_invited_status__to_attending_status__in=statuses).values("user", "to_invited_status__to_attending_status__id")
    for from_status_user in from_status_users:
        queue_writer.response(User.objects.get(id=from_status_user["user"]), AttendingStatus.objects.get(id=from_status_user["to_invited_status__to_attending_status__id"]))

    statuses.update(status=AttendingStatus.ACCEPTED, public=public)


# action options are Invite, Cancel Invitation, Add, Stop Attending, Unable
def make_a_change(user, action, coded_event_id):
    event_id = misc_functions.decode_id(coded_event_id)
    event_dbo = Event.objects.get(id=event_id)

    if action not in EventOption.ALL_OPTIONS:
        raise "unknown option with %s" % action

    if action == EventOption.REMOVE:
        statuses = [AttendingStatus.ADDED, AttendingStatus.ACCEPTED]
        AttendingStatus.objects.filter(event__id=event_id, status__in=statuses,
                                       user=user).update(deleted=True)

    elif action == EventOption.UNABLE:
        statuses = AttendingStatus.objects.filter(
            event__id=event_id, user=user)
        statuses = statuses.filter(
            status__in=[AttendingStatus.INVITED, AttendingStatus.ACCEPTED])
        from_status_users = AttendingStatus.objects.filter(to_invited_status__to_attending_status__in=statuses).values("user", "to_invited_status__to_attending_status__id")
        for from_status_user in from_status_users:
            queue_writer.response(User.objects.get(id=from_status_user["user"]), AttendingStatus.objects.get(id=from_status_user["to_invited_status__to_attending_status__id"]))

        statuses.update(status=AttendingStatus.UNABLE)

    # add in functionality to alert if the user has invited people
    elif action == EventOption.ADD or action == EventOption.ADD_PRIVATELY:
        new_status = AttendingStatus(user=user, status=AttendingStatus.ADDED,
                                     updated=datetime.utcnow())
        new_status.event = event_dbo
        new_status.public = (action == EventOption.ADD)
        new_status.save()

    elif action == EventOption.ACCEPT or action == EventOption.ACCEPT_PRIVATELY:
        accept(user, action, event_dbo)
    else:
        raise "unknown event option with %s" % action
