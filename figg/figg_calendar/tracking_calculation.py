from figg_calendar.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from twitter.models import UserDetails
from mainPage.models import Tag, Venue, EventSeries
from django.contrib.auth.models import User


def select(user, add, venue=None, tag=None, cal=None, series=None):
    """ allows you to add or remove a cal/tag/venue"""
    args = {}
    args["venue"], args["tag"], args["cal"], args["series"] = venue, tag, cal, series
    args["user"] = user

    if venue:
        selected = TrackingVenue.objects.get_or_create(user=user, venue=venue)
    if tag:
        selected = TrackingTag.objects.get_or_create(user=user, tag=tag)
    if cal:
        selected = TrackingCal.objects.get_or_create(user=user, cal=cal)
    if series:
        selected = TrackingSeries.objects.get_or_create(user=user, series=series)

    field = selected[0]

    field.selected = add
    field.save()


class AbstractTo(object):
    def __init__(self, id, name, selected=False, tracking=False):
        self.id = id
        self.name = name
        self.selected = selected
        self.tracking = tracking

    def as_json(self):
        return self.__dict__

    def __repr__(self):
        return "%s: %s %s" % (self.__class__, self.name, self.id)

class CalTo(AbstractTo):
    def __init__(self, id, name, img_mini, img_normal, img_bigger):
        super(CalTo, self).__init__(id, name)

        #we shouldn't have to do this but I think the table needs to be reset before the defaults work
        if img_normal: 
            self.img_mini = img_normal
        else:
            self.img_mini = UserDetails.DEFAULT

        if img_mini: 
            self.img_normal = img_mini
        else:
            self.img_normal = UserDetails.NORMAL_DEFAULT

        if img_bigger: 
            self.img_large = img_bigger
        else:
            self.img_large = UserDetails.LARGE_DEFAULT

    def __repr__(self):
        return "%s: %s %s" % (self.__class__, self.name, self.id)


class TagTo(AbstractTo):
    def __init__(self, id, name):
        super(TagTo, self).__init__(id, name)


class SeriesTo(AbstractTo):
    def __init__(self, id, name):
        super(SeriesTo, self).__init__(id, name)


class VenueTo(AbstractTo):
    def __init__(self, id, name):
        super(VenueTo, self).__init__(id, name)

def mark_as_selected(results, users_selection):
    for result in results:
        result.selected = result.id in users_selection

    return results


def get_tracking_cals(other_user, user):
    """ other user is the user not logged in, user is the user logged in, realistically we should have 3 states, we change it to hidden makes more sense, boo"""
    args = ["cal__id", "cal__username", "cal__user_details__user_img_mini", "cal__user_details__user_img_normal", "cal__user_details__user_img_bigger"]
    query = TrackingCal.objects.filter(user=other_user).values_list(*args)
    results = [CalTo(*i) for i in query]

    if not user:
        return results

    users_selection = set(TrackingCal.objects.filter(user=user, selected=True).values_list("cal__id", flat=True))
    return mark_as_selected(results, users_selection)


def get_tracking_tags(other_user, user):
    args = ["tag__id", "tag__name"]
    query = TrackingTag.objects.filter(user=other_user).values_list(*args)
    users_selection = set(TrackingTag.objects.filter(user=user, selected=True).values_list("tag__id", flat=True))
    results = [TagTo(*i) for i in query]

    if not user:
        return results

    return mark_as_selected(results, users_selection)


def get_tracking_series(other_user, user):
    args = ["series__id", "series__name"]
    query = TrackingSeries.objects.filter(user=other_user).values(*args)
    users_selection = set(TrackingSeries.objects.filter(user=user, selected=True).values_list("series__id", flat=True))
    results = [SeriesTo(*i) for i in query]

    if not user:
        return results
    return mark_as_selected(results, users_selection)


def get_tracking_venues(other_user, user):
    args = ["venue__id", "venue__name"]
    query = TrackingVenue.objects.filter(user=other_user).values(*args)
    users_selection = set(TrackingVenue.objects.filter(user=user, selected=True).values_list("venue__id", flat=True))
    results = [VenueTo(**i) for i in query]
    return mark_as_selected(results, users_selection)


def get_tracking(other_user, user=None):
    """ get all cal tags that the user is following and whether they are selected """

    if other_user == user: 
        title = "You're tracking"
    else:
        title = "%s tracks" % other_user.username

    return {
            "cal": get_tracking_cals(other_user, user),
            "tag": get_tracking_tags(other_user, user),
            "series": get_tracking_series(other_user, user),
            "venue": get_tracking_venues(other_user, user),
            "title": title
            }


def get_trackers(user = None, venue=None, tag=None, cal=None, series=None):
    args = ["user__id", "user__username", "user__user_details__user_img_mini", "user__user_details__user_img_normal", "user__user_details__user_img_bigger"]
    if venue:
        cals = TrackingVenue.objects.filter(venue=venue)
        title = "%s is tracked by" % venue.name
    if tag:
        cals = TrackingTag.objects.filter(tag=tag)
        title = "%s is tracked by" % tag.name
    if cal:
        cals = TrackingCal.objects.filter(cal=cal)
        title = "%s is tracked by" % cal.username
    if series:
        cals = TrackingSeries.objects.filter(series=series)
        title = "tracking this series"

    results = [CalTo(*i) for i in cals.values_list(*args)]

    if not user:
        return {"cal": results}

    users_selection = set(TrackingCal.objects.filter(user=user, selected=True).values_list("cal__id", flat=True))
    return {"cal": mark_as_selected(results, users_selection), "title": title}



def get_selected_users(user, user_ids):
    """ returns all the ids that are selected """
    return TrackingCal.objects.filter(user=user).filter(selected=True).filter(cal__id__in=user_ids).values_list("cal__id", flat=True)


def get_selected_tags(user, tag_names):
    return TrackingTag.objects.filter(user=user).filter(selected=True).filter(tag__name__in=tag_names).values_list("tag__name", flat=True)


def populate_defaults(user):
    for i in Tag.objects.all():
        selected = TrackingTag(user=user)
        selected.tag = i
        selected.save()

    for i in User.objects.filter(is_superuser = False):
        selected = TrackingCal(user=user)
        selected.cal = i
        selected.save()

def get_trackee_count(user):
    """ returns the amount of things this user is tracking """
    cals = TrackingCal.objects.filter(user=user).count()
    tags = TrackingTag.objects.filter(user=user).count()
    venues = TrackingVenue.objects.filter(user=user).count()
    series = TrackingSeries.objects.filter(user=user).count()
    return cals + tags + venues + series

def get_related_tags(user=False, cal=None, venue=None, series=None):
    """get's all tags connected, for the user this is the tags they've made for tags its non existent, for series and venue its events that are tagged with that there"""
    args = ["id", "name"]

    if cal:
        title = "tags used by %s" % cal.username
        tags = Tag.objects.filter(cals=cal)
    if venue:
        title = "events at %s have been tagged with"
        tags = Tag.objects.filter(events__venue=venue)
    if series:
        title = "events in this series have been tagged with"
        tags = Tag.objects.filter(events__event_series = series)

    results = [TagTo(*i) for i in tags.values_list(*args)]

    if not user:
        return {"tag": results, "title": title}

    users_selection = set(TrackingTag.objects.filter(user=user).values_list("tag__id", flat=True))
    return {"tag": mark_as_selected(results, users_selection), "title": title}


def get_tracking_count(field):

    if isinstance(field, Tag):
        return TrackingTag.objects.filter(tag=field).count()
    elif isinstance(field, User):
        return TrackingCal.objects.filter(cal=field).count()
    elif isinstance(field, EventSeries):
        return TrackingSeries.objects.filter(series=field).count()
    elif isinstance(field, Venue):
        return TrackingVenue.objects.filter(series=field).count()

def remove(user, venue=None, tag=None, cal=None, series=None):
    """ needs to be changed to pass ids back """
    if venue != None:
        TrackingVenue.objects.filter(user=user, venue=venue).delete()

    if tag != None:
        TrackingTag.objects.filter(user=user, tag=tag).delete()
    
    if cal != None:
        TrackingCal.objects.filter(user=user, cal=cal).delete()

    if series != None:
        TrackingSeries.objects.filter(user=user, series=series).delete()

@receiver(post_save, sender=User)
def on_user_create(sender, instance, created, **kwargs):
    if created:
        populate_defaults(instance)











