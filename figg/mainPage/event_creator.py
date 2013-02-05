from mainPage.models import AttendingStatus, Event, EventImage, Venue, EventSeries
from django.utils.html import strip_tags
from mainPage import preview_calculation, tag_calculation, event_key, note_calculation
from common.figgDate import FiggDate
from event_calculation import process_img
from datetime import datetime


def submit_event(event_date, title, description, user, event_time=None, event_venue=None, invited=[], public=False, repeat_regularity=None, repeat_until=None, img=None, img_id=None):

    if (repeat_until and not repeat_regularity) or (not repeat_until and repeat_regularity):
        raise EventCreationException("invalid submit event args %s" % locals())

    if img:
        event_img = process_img(img)
    elif img_id:
        event_img = EventImage.objects.get(id=img_id)
    else:
        event_img = None

    if description:
        cleaned_description = strip_tags(description)
    else:
        cleaned_description = None

    cleaned_title = strip_tags(title).strip()

    if repeat_regularity:
        event_times = preview_calculation.times_calculation(
            repeat_regularity, event_date, event_time, repeat_until)
    else:
        figg_date = FiggDate(event_date, event_time)
        event_times = [figg_date]

    if event_venue:
        venue = Venue.objects.get(id=event_venue)
    else:
        venue = None    

    uncommitted_events = []
    updated = datetime.now()

    for event_time in event_times:
        event = translate_event_time_to_event(event_time, cleaned_description, cleaned_title, venue, public, event_img, updated)
        uncommitted_events.append(event)

    create_events(uncommitted_events, user, updated, public, invited)


def create_events(uncommitted_events, user, updated, public=True, invited=None):

    attending_statuses = []
    events = []

    for event in uncommitted_events:
        event.save()
        created = AttendingStatus(status=AttendingStatus.CREATOR, event=event,
                                  user=user, public=public, updated=updated)
        added = AttendingStatus(status=AttendingStatus.ADDED, event=event,
                                user=user, public=public, updated=updated)
        attending_statuses.extend([added, created])
        events.append(event)

    AttendingStatus.objects.bulk_create(attending_statuses)

    if len(events) > 1:
        event_series = EventSeries()
        event_series.save()
        event_series.event_set.add(*events)

    for event in events:
        if invited:
            note_calculation.invite(user, invited, event)
    tag_calculation.save_tags_for_events(user, events)


def translate_event_time_to_event(event_time, cleaned_description, cleaned_title, venue, public, event_img, updated):
    event = Event()
    event.key = event_key.create_date_key(event_time.date, event_time.time)
    event.date = event_time.date
    event.time = event_time.time
    event.description = cleaned_description
    event.title = cleaned_title
    event.venue = venue
    event.public = public
    event.img = event_img
    event.updated = updated

    return event


class EventCreationException(Exception):
    pass
