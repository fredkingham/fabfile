from datetime import datetime, timedelta
from mainPage.models import Venue, EventTime
from django.utils import simplejson
import urllib, urllib2
from django.contrib.auth.models import User
cinema_url = "http://www.cineworld.co.uk/api/quickbook/cinemas?key=GrY3yUFp&full=true&territory=GB"
performances_url = "http://www.cineworld.com/api/quickbook/performances?key=GrY3yUFp&cinema=%s&date=%s&film=%s"
date_url = "http://www.cineworld.com/api/quickbook/dates?key=GrY3yUFp&cinema=%s"
film_url = "http://www.cineworld.com/api/quickbook/films?key=GrY3yUFp&cinema=%s"

from mainPage import event_calculation, venue_calculation
from collections import defaultdict
username = "figg_film"
cinema_user = User.objects.get(username = username)
import re


def is_london_postcode(postcode):
    areas = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]

    for area in areas:
        regex = r'\A%s\d' % area
        search_result = re.search(regex, postcode)

        if search_result:
            return True

    return False

def load_venues():

    venues = []
    cinema_result = read(cinema_url)
    cinemas = cinema_result["cinemas"]

    id_to_venue = {}

    for cinema in cinemas:
        name = "cineworld %s" % cinema[u'name'][:50] 
        address = cinema[u'address'].split(",", 1)[0]
        postcode = cinema[u'postcode']

        if not is_london_postcode(postcode):
            continue

        if name == "Hammersmith":
            continue


        public = True

        venues = Venue.objects.filter(name = name)

        if not venues:
            venue_calculation.submit_venue(name, address, postcode, public, username)

        id_to_venue[cinema["id"]] = Venue.objects.get(name = name)

    return id_to_venue

def read(url):
    url_handler = urllib2.urlopen(url)
    response = url_handler.read()
    url_handler.close()
    return simplejson.loads(response)
    
    


def load_film_times(venue_map):

    event_times = []
    title_to_event = defaultdict(list)
    description = "#film"

    for venue_id in venue_map:
        dates_for_cinema = date_url % venue_id
        film_url_for_dates = film_url % venue_id
        films = read(film_url_for_dates)["films"]
        event_times = []

        for film in films:
            print "venue %s film %s" % (venue_map[venue_id].name, film)
            dates = read(dates_for_cinema)["dates"]

            for date in dates:
                formatted_performances_url = performances_url % (venue_id, date, film["edi"] )
                try:
                    performances = read(formatted_performances_url)["performances"]
                except:
                    print "erroring for %s" % performances_url


                for performance in performances:
                    event_time = {}
                    event_time["venue"] = venue_map[venue_id]
                    event_time["date"] = datetime.strptime(str(date), "%Y%m%d").date()
                    event_time["time"] = datetime.strptime(str(performance["time"]), "%H:%M").time() 
                    existing = EventTime.objects.filter(venue__id = venue_id)
                    existing = existing.filter(date = event_time["date"])
                    existing = existing.filter(time = event_time["time"])
                    existing = existing.filter(event__title = film["title"])

                    if not len(existing):
                        title_to_event[film["title"]].append(event_time)
                    else:
                        print "found %s for %s %s" % (film["title"], event_time["date"], event_time["venue"])

    for title, event_times in title_to_event.items():
        pertinent = ["2D", "3D"]
        regex = r"\A\W%s\W\Z" 
        film_description = description

        for pert in pertinent:
            search = re.search(regex % pert, title)
            if search:
                film_description = "%s #%s" % (description, pert)

        
        event_calculation.create_events(cinema_user, event_times, title, film_description, [], True)

def load_films():
    venue_map = load_venues()
    load_film_times(venue_map)


#def load_cinemas():
#
#    for cinema in cinemas:
#        if cinema[u'name'] not in cinemas_to_add:
#            continue
#
#        venue_info = {}
#        venue_info["name"] = "cineworld, %s" % cinema[u'name'] 
#        venue_info["address"] = cinema[u'address'].split(",", 1)[0]
#        venue_info["postcode"] = cinema[u'postcode']
#        venue_info["public"] = True
#        venue_info["website"] = cinema[u'cinema_url']
#
#        venue = Venue.objects.get_or_create(**venue_info)[0]
#        store_long_lat(venue.address, venue.postcode)
#
#        cinema_id = cinema["id"]
#        dates_for_cinema = date_url % cinema_id
#        dates = simplejson.load(urllib.urlopen(dates_for_cinema))["dates"]
#
#        film_url_for_dates = film_url % cinema_id
#        
#        for date in dates:
#            film_url_for_dates += "&date=" + date
#
#        films = simplejson.load(urllib.urlopen(film_url_for_dates))["films"]
#
#        for film in films:
#
#            event_times = []
#
#            for date in dates:
#                formatted_performances_url = performances_url % (cinema_id, date, film["edi"] )
#                performances = simplejson.load(urllib.urlopen(formatted_performances_url))["performances"]
#
#                for performance in performances:
#                    performance_date = datetime.strptime(str(date), "%Y%m%d").date()
#                    film_time = str(performance["time"])
#                    time = datetime.strptime( film_time, "%H:%M").time()
#                    description = "#film" % film["title"]
#                    event_times.append(venue, performance_date, time)
#                
#
#
#        if not Event.objects.filter(date = performance_date, time = time, description = description):
#            event_calculation.create_event(performance_date, time, description, "F_i_g_g", [], True, venue)
#            
#def get_event_times(venue, date, time):
#    return locals()
