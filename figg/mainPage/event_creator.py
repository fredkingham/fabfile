from mainPage.models import AttendingStatus, Event, EventImage, Venue, EventSeries
from django.utils.html import strip_tags
from mainPage import preview_calculation, tag_calculation, event_key, note_calculation
from common.figgDate import FiggDate
from event_calculation import process_img

def submit_event(event_date, title, description, user, event_time = None, event_venue = None, invited = [], public = False, repeat_regularity = None, repeat_until = None, img = None, img_id = None):

    if (repeat_until and not repeat_regularity) or (not repeat_until and repeat_regularity):
        raise EventCreationException("invalid submit event args %s" % locals())

    if img:
        event_img = process_img(img)
    elif img_id:
        event_img = EventImage.objects.get(id = img_id)
    else:
        event_img = None

    if description:
        cleaned_description = strip_tags(description)
    else:
        cleaned_description = None
    
    cleaned_title = strip_tags(title).strip()

    if repeat_regularity: 
        event_times = preview_calculation.times_calculation(repeat_regularity, event_date, event_time, repeat_until)
    else:
        figg_date = FiggDate(event_date, event_time)
        event_times = [figg_date]

    if event_venue:
        venue = Venue.objects.get(id = event_venue)
    else:
        venue = None

    events = []

    for event_time in event_times:
        event = Event()
        event.key = event_key.create_date_key(event_time.date, event_time.time)
        event.date = event_time.date
        event.time = event_time.time
        event.description = cleaned_description
        event.title = cleaned_title
        event.venue = venue
        event.public = public
        event.img = event_img
        event.save()
        events.append(event)
        created = AttendingStatus(status = AttendingStatus.CREATOR, event = event, user = user, public = public)
        created.save()
        added = AttendingStatus(status = AttendingStatus.ADDED, event = event, user = user, public = public)
        added.save()
        if invited:
            note_calculation.invite(user, invited, event)
        tag_calculation.save_tags_for_events(cleaned_title, cleaned_description, user, event)

    if len(events) > 1:
        event_series = EventSeries()    
        event_series.save()
        event_series.event_set.add(*events)

class EventCreationException(Exception):
    pass



