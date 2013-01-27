from mainPage.models import Venue, VenueOwner
from django.utils import simplejson
import urllib2
from threading import Thread
from django.db.models import Q

def get_venues(start_string, username = False):

    query = Venue.objects.filter(Q(name__istartswith = start_string) | Q(postcode__istartswith = start_string))
    
    if start_string:
        query = query.filter(Q(public = 1) | Q(Q(public = 0) & Q(venueowner__user = username)))
        query = query.values("public", "name", "postcode", "id")
        result = []
        for row in query:
            if row["public"]:
                name = row["name"]
            else:
                name = "%s (private)" % row["name"]

            text_name = "%s (%s)" % (name, row["postcode"])
            result.append({"label": text_name, "id": row["id"]})
            #result.append(text_name)

    return result

def submit_venue(name, address, postcode, public, creator):
    if not public:
        public = True

    new_venue = Venue.objects.get_or_create(name = name, address = address, postcode = postcode, public = public, creator = creator)

    if public and new_venue[1]:
       VenueOwner.objects.get_or_create(venue = new_venue[0], user = creator)  

    spawn_lat_long_populate(address, postcode)

    return new_venue

def calculate_venue_structure(name_postcode):
    venue = get_venue_model(name_postcode)
    if not venue:
        return False
    if venue.public == True:
        return {"venue": venue}
    else:
        return {"venue": venue, "venue_privacy": get_venue_owner(venue)}
        
def get_venue_owner(venue):
    all_venue_owners = VenueOwner.objects.filter(venue = venue)

    return map(lambda x: x.user, all_venue_owners)


# name_postcode should be of the form The_Red_Lion
def get_venue_model(name_postcode_without_spaces):

    name_postcode = name_postcode_without_spaces.replace("_", " ")
    split = name_postcode.rsplit("-", 1)

    if len(split) == 2:
        ven = Venue.objects.filter(name = split[0], postcode = split[1])
        
        if len(ven):
            return ven[0]
    
    ven = Venue.objects.filter(name = name_postcode) 

    if len(ven):
        return ven[0]

    return False

# get the longitude and latitude of a postcode from the google apis service,
# store it in our database
# google api seems to have country so... do we need to store country, I'd like
# to compare the 2 for sanity check...
def get_long_lat(address, postcode):
    url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s, %s&sensor=false" % (address, postcode)
    url = url.replace(" ", "")
    response_string = urllib2.urlopen(url).read()
    response = simplejson.loads(response_string)

# handle exception case
    if "status" in response and response["status"] == 'OK' and "results" in response and len(response["results"]):
        if len(response["results"]) and "geometry" in response["results"][0]:
            geometry = response["results"][0]["geometry"]
            if "location" in geometry and "lat" in geometry["location"] and "lng" in geometry["location"]:
                return {"lat": geometry["location"]["lat"], "lng": geometry["location"]["lng"] }

    raise Exception("unable to find addrss for %s %s" % (address, postcode))

def save_long_lat(address, postcode, lat, lng):
    venues = Venue.objects.filter( address = address, postcode = postcode )

    for venue in venues:

        changed = False
        if not venue.latitude or not venue.longitude:
            venue.latitude = lat
            venue.longitude = lng
            changed = True

        if not changed and (venue.latitude != lat or venue.longitude != lng):
            venue.latitude = lat
            venue.longitude = lng
            changed = True

        if changed:
            print "data stored for %s %s" % (address, postcode)
            venue.save()
        else:
            print "data not stored as it hasn't changed %s %s" % (address, postcode)

# starts a daemon thread and tries to store the data
def spawn_lat_long_populate(address, postcode):
    t = Thread( target = store_long_lat, args=(address, postcode) )    
    t.daemon = True
    t.start()


def store_long_lat(address, postcode):
    long_lat = get_long_lat(address, postcode)
    save_long_lat(address, postcode, long_lat["lat"], long_lat["lng"])

def update_long_lats():
    venues = Venue.objects.filter( latitude = None )

    for venue in venues:
        spawn_lat_long_populate(venue.address, venue.postcode)


    venues = Venue.objects.filter( longitude = None )

    for venue in venues:
        spawn_lat_long_populate(venue.address, venue.postcode)

def get_venue_for_id(venue_id):
    return Venue.objects.get(id = venue_id).as_dict()

def get_venue_from_id(id):
    return Venue.objects.get(id = id)

def get_venue_from_name(name):
    return Venue.objects.get(name = name)

