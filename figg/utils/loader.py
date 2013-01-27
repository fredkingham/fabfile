from mainPage import venue_calculation, event_calculation
from mainPage.models import *
from datetime import timedelta

class Loader(object):

    def load_venues(self, venues):
        fields = ["name", "address", "postcode", "public", "creator"]
        for venue in venues:
            for field in fields:
                if field not in venue:
                    raise "missing required field %s" % field

            existing = Venue.objects.filter(**venue)

            if existing:
                print "we already have this venue %s" % existing
            else:
                venue_calculation.submit_venue(**venue)

    def load_events(self, title, user, event_times, venue_map = False, description = None):
        existing = Event.objects.filter(title = title, event_times__attendingstatus = user)

        if venue_map:
            venues = Venue.objects.filter(**venue_map)
            if len(venues) != 1:
                raise "incorrect amount of venues passed in"
            venue = venues[0]

        for event_time in event_times:
            if "venue" not in event_time and venue_map:
                event_time["venue"] = venue

        if existing:
            if len(existing > 1):
                raise "we've got multiple events of this name!"
            else:
                event = existing[0]
                for event_time in event_times:
                    existing_times = EventTimes.filter(event = event, date = event_time["date"], time = event_time["time"])
                    if existing_times:
                        print 'we already have this one for %s %s' % (event.title, event_times)
                    else:
                        print "creating eventtimes for " % event
                        event_calculation.add_event_times(existing[0], event_times, user)
        else:
            print "creating event for %s" % title
            event_calculation.create_events(user, event_times, title, description.strip(), [], True)

    def dateTimesForRange(self, from_date, to_date, time, excluding = [], including = []):
        ''' excluding and only are weekdays as given by datetime.weekday'''

        print "getting load times"
        if len(excluding) and len(including):
            raise "you want us to include and exclude, that's not possible"
        event_times = []

        while from_date < to_date:
            if excluding and from_date.weekday() in excluding:
                from_date = from_date + timedelta(1)
                continue

            if including and from_date.weekday() not in including:
                from_date = from_date + timedelta(1)
                continue

            else:
                event_times.append({"date": from_date, "time": time})

            from_date = from_date + timedelta(1)

        print "returning load times"

        return event_times




