from figg_calendar import tracking_calculation
from mainPage import event_calculation, tag_calculation
from twitter import user_calculation
from twitter import BIGGER
from twitter.models import UserDetails
from mainPage.models import Event, AttendingStatus
from figg_calendar.models import TrackingCal, TrackingSeries, TrackingTag


class AbstractProfile(object):
    """ defines the left hand bar for cals/tags/series """
    def __init__(self, field):
        self.id = field.id
        self.tracking_count = tracking_calculation.get_tracking_count(field)

    def as_json(self):
        return self.__dict__

class CalProfile(AbstractProfile):
    def __init__(self, field, user):
        super(CalProfile, self).__init__(field)
        self.name = field.username
        self.img = user_calculation.get_imgs([self.name], BIGGER)[self.name]
        self.event_count = event_calculation.get_event_count(field)

        if UserDetails.objects.filter(user__username=field).exists():
            self.description = UserDetails.objects.get(user__username=field).description
        else:
            self.description = ""
        #how many calendars is this user tracking
        self.trackee_count = tracking_calculation.get_trackee_count(field)
        # we need the trackee count in here
        self.tag_count = tag_calculation.get_user_tag_count(field)
        self.selected = TrackingCal.objects.filter(cal=field, user=user, selected=True).count() > 0

class TagProfile(AbstractProfile):
    def __init__(self, field, user):
        super(TagProfile, self).__init__(field)
        self.name = field.name
        self.event_count = tag_calculation.get_event_tag_count(self.name)
        self.selected = TrackingTag.objects.filter(tag=field, user=user, selected=True).count() > 0

class SeriesProfile(AbstractProfile):
    def __init__(self, field, user):
        super(SeriesProfile, self).__init__(field)
        events = Event.objects.filter(event_series=field, deleted=False)
        self.selected = TrackingSeries.objects.filter(series=field, user=user, selected=True).count() > 0

        if not events:
            raise Exception("unable to find any events for this series")

        event = events[0]
        self.name = event.title

        if event.img:
            self.img = event.img.large_img.url
        else:
            self.img = AttendingStatus.objects.get(event=event.id, status=AttendingStatus.CREATOR).user.user_details.user_img_bigger

        self.event_count = len(events)

    def __repr__(self):
        return "%s: %s %s %s %s %s" % (self.__class__.__name__, self.name, self.id, self.tracking_count, self.img, self.event_count)


def get_profile(cal, venue, series, tag, user = None):
    if cal:
        return CalProfile(cal, user)
    if tag:
        return TagProfile(tag, user)
    if series:
        return SeriesProfile(series, user)
