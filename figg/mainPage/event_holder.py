from django.db.models import Q
import operator
from mainPage import event_key
from mainPage.models import AttendingStatus
from mainPage.models import Event as EventDB
from mainPage.event import Event, NotLoggedInEvent
from figg_calendar.models import TrackingCal, TrackingTag, TrackingSeries

DEFAULT_CAP = 20 


class AbstractEventHolder(object):
    
    @classmethod
    def empty_result(self):
        return {"events": [], "more": False, "previous": False}

    def __init__(self, start_date=False, end_date=False, cap=DEFAULT_CAP, user=False, start_key=False, end_key=False):
        self.start_date = start_date
        self.user = user
        self.events = {}
        self.cap = cap
        self.more = False
        self.end_date = end_date
        self.start_key = start_key
        self.end_key = end_key

        if not start_key and start_date:
            #generate a start key, -1 because start_date is inclusive
            self.start_key = event_key.date_key(start_date) -1

        if not end_key and end_date:
            self.end_key = event_key.date_key(end_date)

        self.initial_load = not start_key and not end_key and not end_date

        if self.initial_load:
            self.previous = False

    def populate(self):
        events = self.get_events()
        self.events = self.sort_and_cap_events(events, self.cap)
        self.previous = self.are_there_previous(self.events)
        self.more = self.are_there_more(self.events)

    def get_events(self):
        events = self.get_user_events(self.start_key, self.end_key, self.user)
        preexisting = [i.event_id for i in events]
        relevent_events = self.get_relevent_events(self.start_key, self.end_key, self.user, preexisting)
        events.extend(relevent_events)
        for event in events:
            event.user = self.user

        return events

    def sort_and_cap_events(self, events, cap):
        return (sorted(events, key=lambda k: k.event_date))[:cap]

    def are_there_previous(self, events):
        """ we look at the existing events and use direction down and the
        lowest key and run exists """

        if events:
            lowest_key = min([i.time_key for i in events])
        elif self.start_key:
            lowest_key = self.start_key
        elif self.end_key:
            lowest_key = self.end_key - 1
        else:
            return []

        user_previous = self.get_user_events_query(False, lowest_key, self.user)

        if not user_previous:
            return self.get_relevent_events_query(False, lowest_key, []).exists()
        return True

    def are_there_more(self, events):
        if events:
            highest_key = max([i.time_key for i in events])
        elif self.end_key:
            highest_key = self.end_key
        elif self.start_key:
            highest_key = self.start_key + 1
        else:
            return []

        user_more = self.get_user_events_query(highest_key, False, self.user)

        if not user_more:
            return self.get_relevent_events_query(highest_key, False, []).exists()
        else:
            return True

    def remap_fields(self, results, fields):
        remapped_events = []

        for result in results:
            remapped = {}
            for key, value in fields.items():
                remapped[value] = result[key]
            remapped_events.append(remapped)

        return remapped_events

    def get_relevent_events_query(self, highest_key, lowest_key, preexisting):
        raise "abstract method this should not be called"

    def get_user_events_query(self, highest_key, lowest_key, preexisting):
        raise "abstract method this should not be called"

    def get_relevent_events(self, start_key, end_key, user, event_ids):
        query = self.get_relevent_events_query(start_key, end_key, event_ids)
        query = self.order_event_times(query, start_key, end_key)

        results = query[:self.cap]

        fields = {}
        fields["public"] = "public"
        fields["id"] = "event_id"
        fields["description"] = "description"
        fields["title"] = "title"
        fields["date"] = "event_date"
        fields["time"] = "event_time"
        fields["venue__id"] = "venue_id"
        fields["deleted"] = "deleted"
        fields["key"] = "time_key"
        fields["event_series"] = "series"

        keys = fields.keys()
        results_from_keys = results.values(*keys)

        values = self.remap_fields(results_from_keys, fields)

        if self.user:
            events = [Event(**x) for x in values]
        else:
            events = [NotLoggedInEvent(**x) for x in values]

        return events



    def order_event_times(self, query, start_key, end_key):
        if self.start_key:
            query = query.order_by("key")
        else:
            query = query.order_by("-key")
        return query

    def filter_event_times(self, query, start_key, end_key):
        if start_key:
            query = query.filter(key__gt=start_key)

        if end_key:
            query = query.filter(key__lt=end_key)

        return query


    def get_user_events(self, start_key, end_key, user):
        query = self.get_user_events_query(start_key, end_key, user)
        query = self.order_event_times(query, start_key, end_key)

        fields = {}
        fields["public"] = "public"
        fields["id"] = "event_id"
        fields["description"] = "description"
        fields["title"] = "title"
        fields["date"] = "event_date"
        fields["time"] = "event_time"
        fields["venue__id"] = "venue_id"
        fields["deleted"] = "deleted"
        fields["key"] = "time_key"
        fields["event_series"] = "series"
        results = query[:self.cap]

        keys = fields.keys()
        results_from_keys = results.values(*keys)

        values = self.remap_fields(results_from_keys, fields)

        for i in values:
            i["belongs_to_user"] = True

        events = list(set([Event(**x) for x in values]))

        statuses = {}
        for x in events:
            statuses[x.event_id] = x

        status_query = AttendingStatus.objects.filter(event__id__in=statuses.keys())
        status_query = status_query.filter(user=user)
        values = status_query.values("event__id", "status")

        for i in values:
            statuses[i["event__id"]].statuses.append(AttendingStatus.ATTENDING_STATUS_CHOICES[i["status"]])

        return events

    def as_json(self):
        return {
                    "events": self.events,
                    "more": self.more,
                    "previous": self.previous
                }


class SeriesEventHolder(AbstractEventHolder):
    def __init__(self, series, start_date=False, end_date=False, cap=DEFAULT_CAP, user=False, start_key=False, end_key=False):
        super(SeriesEventHolder, self).__init__(start_date, end_date, cap, user, start_key, end_key)
        self.series = series

    def get_user_events_query(self, start_key, end_key, user):
        query = EventDB.objects.filter(attending_status__user=user).filter(deleted=False)
        query = self.filter_event_times(query, start_key, end_key)
        query = query.filter(attending_status__status__in=AttendingStatus.USER_DISPLAY)
        query = query.filter(event_series__id=self.series)
        return query.distinct()

    def get_relevent_events_query(self, start_key, end_key, event_ids):
        query = EventDB.objects.filter(deleted=False)
        query = self.filter_event_times(query, start_key, end_key)
        query = query.filter(attending_status__status__in=AttendingStatus.DISPLAY)
        query = query.filter(event_series__id=self.series)
        return query.distinct()


class SpecificEventHolder(AbstractEventHolder):
    def __init__(self, start_date=False, end_date=False, cap=DEFAULT_CAP, user=False, start_key=False, end_key=False, cal=False, tag=False):
        super(SpecificEventHolder, self).__init__(start_date, end_date, cap, user, start_key, end_key)
        self.cal = cal
        self.tag = tag
        if not cal and not tag:
            raise Exception("no cal or tag passed to the event holder")

    def get_user_events_query(self, start_key, end_key, user):
        cal = self.cal
        tag = self.tag
        query = EventDB.objects.filter(attending_status__user=user).filter(deleted=False)
        query = self.filter_event_times(query, start_key, end_key)
        query = query.filter(attending_status__status__in=AttendingStatus.USER_DISPLAY)

        if tag:
            query = query.filter(Q(tags__name__iexact=tag) | Q(note__event__note__description__iexact=tag))

        if cal:
            query = query.filter(attending_status__user__username=cal)

        return query.distinct()

    def get_relevent_events_query(self, start_key, end_key, event_ids):
        print "locals %s" % locals()
        cal = self.cal
        tag = self.tag
        query = EventDB.objects.filter(deleted=False)
        query = self.filter_event_times(query, start_key, end_key)
        query = query.filter(attending_status__status__in=AttendingStatus.DISPLAY)
        if tag:
            query = query.filter(Q(tags__name__iexact=tag) | Q(note__event__note__description__iexact=tag))

        if cal:
            query = query.filter(attending_status__user__username=cal)

        return query.distinct()


class EventHolderForUser(AbstractEventHolder):
    def __init__(self, start_date=False, end_date=False, cap=DEFAULT_CAP, user=False, start_key=False, end_key=False):
        super(EventHolderForUser, self).__init__(start_date, end_date, cap, user, start_key, end_key)
        self.selected_cals = TrackingCal.objects.filter(user=user, selected=True).values_list("cal", flat=True)
        self.selected_tags = TrackingTag.objects.filter(user=user, selected=True).values_list("tag__name", flat=True)
        self.selected_series = TrackingSeries.objects.filter(user=user, selected=True).values_list("series__id")

    def get_relevent_events_query(self, start_key, end_key, event_ids):
        print "locals %s" % locals()
        print "selected cals %s" % self.selected_cals
        print "tags %s" % self.selected_tags
        query = EventDB.objects.filter(deleted=False)
        query = query.filter(attending_status__status__in=AttendingStatus.DISPLAY)

        q_list = []
        if self.selected_cals:
            q_list.append(Q(attending_status__user__id__in=self.selected_cals))

        for tag in self.selected_tags:
            q_list.append(Q(tags__name__iexact=tag))
            q_list.append(Q(note__event__note__description__iexact=tag))        

        if self.selected_series:
            q_list.append(Q(event_series__id__in = self.selected_series))

        if q_list:
            query = query.filter(reduce(operator.or_, q_list))

        query = query.exclude(id__in=event_ids)
        query = self.filter_event_times(query, start_key, end_key)
        query = query.distinct()

        return query

    def get_user_events_query(self, start_key, end_key, user):
        user = self.user
        query = EventDB.objects.filter(attending_status__user=user).filter(deleted=False)
        query = self.filter_event_times(query, start_key, end_key)
        query = query.filter(attending_status__status__in=AttendingStatus.USER_DISPLAY)
        print "events are %s" % query
        q_list = []
        if self.selected_cals:
            print "we have cals"
            q_list.append(Q(attending_status__user__id__in=self.selected_cals))

        for tag in self.selected_tags:
            print "we have tags"
            q_list.append(Q(tags__name__iexact=tag))
            q_list.append(Q(note__event__note__description__iexact=tag))  

        print "we have a query %s" % q_list
        if q_list:
            print "we then go in here"
            query = query.filter(reduce(operator.or_, q_list))

        print "we have no query %s" % q_list

        query = query.distinct()
        return query


class SearchHolder(AbstractEventHolder):

    def __init__(self, search_term, start_date=False, up=True, end_date=False, start_key=False, end_key=False, user=False, cap=DEFAULT_CAP):
        super(SearchHolder, self).__init__(start_date, end_date, cap, user, start_key, end_key)
        self.search_term = search_term

    def get_relevent_events_query(self, start_key, end_key, event_ids):
        ''' for user isn't used, we'll change this later...'''
        query = EventDB.objects.filter(deleted=False)
        query = query.filter(public=True)
        q_list = []
        q_list.append(Q(title__icontains=self.search_term))
        q_list.append(Q(description__icontains=self.search_term))
        q_list.append(Q(venue__name__icontains=self.search_term))
        q_list.append(Q(venue__postcode__icontains=self.search_term))
        query = query.filter(reduce(operator.or_, q_list))
        query = query.exclude(id__in=event_ids)
        query = self.filter_event_times(query, start_key, end_key)
        return query

    def get_user_events_query(self, start_key, end_key, user):
        query = EventDB.objects.filter(attending_status__user=user).filter(deleted=False)
        query = query.filter(attending_status__status__in=AttendingStatus.USER_DISPLAY)
        q_list = []
        q_list.append(Q(title__icontains=self.search_term))
        q_list.append(Q(description__icontains=self.search_term))
        q_list.append(Q(venue__name__icontains=self.search_term))
        q_list.append(Q(venue__postcode__icontains=self.search_term))
        query = query.filter(reduce(operator.or_, q_list))
        query = self.filter_event_times(query, start_key, end_key)
        return query


class EventHolderByStatus(AbstractEventHolder):
    """doesn't care about date, just get me events from these status ids"""
    def __init__(self, statuses, user):
        self.statuses = statuses
        super(EventHolderByStatus, self).__init__()
        self.user = user

    def get_user_events_query(self, start_key, end_key, user):
        query = EventDB.objects.filter(attending_status__user=user)
        query = query.filter(attending_status__id__in=self.statuses)
        return query

    def get_relevent_events_query(self, start_key, end_key, event_ids):
        query = EventDB.objects.filter(attending_status__id__in=self.statuses)
        query = query.exclude(id__in=event_ids)
        return query
