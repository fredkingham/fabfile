from bs4 import BeautifulSoup
import urllib
from datetime import datetime, date, timedelta
from twitter.data_extract import get_time, add_months, extract_text
from mainPage.models import Venue, AttendingStatus, EventImage
from django.contrib.auth.models import User
from mainPage import event_creator, venue_calculation
from PIL import Image
import urllib, cStringIO
from django.core.files import File
import os


class EventExtract(object):

    def __init__(self, title, date, origin, user, time = None, description = None, link = None, venue = None, img_url = None):
        self.title = title
        self.date = date
        self.time = time
        self.description = description
        self.link = link
        self.venue = venue
        self.user = user
        self.img_url = img_url

    def __unicode__(self):
        repr_str =  "title: %s \n \t date: %s \n \t time: %s \n \t description: %s \n \t link: %s \n \t venue %s" 
        return repr_str % (self.title, self.date, self.time, self.description, self.link, self.venue)

    def __repr__(self):
        repr_str =  "title: %s \n \t date: %s \n \t time: %s \n \t description: %s \n \t link: %s \n \t venue %s" 
        result = repr_str % (self.title, self.date, self.time, self.description, self.link, self.venue)
        return result.encode("utf-8")

    def save(self):
        title = self.title[:100]

        if len(title) > 100:
            description = "%s %s. Read More %s" % (self.title[100:], self.description, self.link)

            if len(description) > 250:
                description = "%s. Read More %s" % (self.title, self.link)

            if len(description) > 250:
                description = "... Read More %s" % self.link
        else:
            description = "%s. Read More %s" % (self.description, self.link)
            if description > 250:
                description = "Read more %s" % self.link

        query = AttendingStatus.objects.filter(user = self.user, event__date = self.date)
        query = query.filter(event__time = self.time, event__title = title)
        query = query.filter(deleted = False)

        if not query.exists():
            if self.img_url:
                result = urllib.urlretrieve(self.img_url)
                event_img = EventImage()
                event_img.img.save(os.path.basename(self.img_url), File(open(result[0], 'rb')))
                event_img.save()
                img_id = event_img.id
            else:
                img_id = None

            event_creator.submit_event(self.date, title, description, self.user, self.time, self.venue.id, public = True, img_id = img_id)


def get_one(collection):
    assert(len(collection) == 1)
    return collection[0]

def pcc_extract():
    query_url = "http://www.princecharlescinema.com/allfilms.php"
    url = "http://www.princecharlescinema.com"
    venue_name = "The Prince Charles Cinema"
    venue = Venue.objects.get(name = venue_name, public = True)
    user = User.objects.get(username = "figg_film")
    f = urllib.urlopen(query_url)
    html = f.read()
    soup = BeautifulSoup(html)
    event_extracts = []
    tables = soup.find_all("table", attrs = {"width": "490px"})
    for i in tables:
        unclean_dates = i.find_all("td", attrs = {"valign": "top"})
        unclean_title = get_one(i.find_all("td", "title490BLACK"))
        unneeded_link = unclean_title.find_all("a")[0].text
        title = unclean_title.text.replace(unneeded_link, "").rstrip().rstrip("-").strip()
        img_url = get_one(i.find_all("img"))["src"]
        description = ""

        for d in i.find_all("span", "buylink"):
            description = "%s %s" % (description, d.text.strip())


        for unclean_date in unclean_dates:
            time_links = unclean_date.find_all("a")
            times = [x.text.strip() for x in time_links]

            for time_link in time_links:
                time = time_link.text.strip()
                link = time_link.attrs["href"]
                date_text = unclean_date.text
                for x in times:
                    date_text = date_text.replace(x, "")

                wrong_date = datetime.strptime(date_text.strip(), "%d/%m")
                today = date.today()
                # if its the next year then we expect the month difference to
                # be massive (this feed is only meant to be the next month)
                if wrong_date.month >= today.month:
                    year = today.year
                elif wrong_date.month + 5 < today.month:
                    continue
                else:
                    year = year + 1

                fixed_date = date(year, wrong_date.month, wrong_date.day)
                fixed_time = get_time(time)
                fixed_link = "%s/%s" % (url, link)

                assert(fixed_time)
    
                event_extracts.append(EventExtract(title, fixed_date, "ThePCCLondon", user, fixed_time, description, fixed_link, venue, img_url = img_url))

    print "event extracts are %s" % event_extracts

    for i in event_extracts:
        i.save()


def national_theatre_extract():
    user = User.objects.get(username = "figg_theatre")
    Cottesloe_Theatre = {"name": "Cottesloe Theatre", "address": "The South Bank", "postcode": "SE1 9PX", "public": True, "creator": user}
    Lyttelton_Theatre = {"name": "Lyttelton Theatre", "address": "The South Bank", "postcode": "SE1 9PX", "public": True, "creator": user}
    Djanogly_Concert_Pitch = {"name": "Djanogly Concert Pitch", "address": "The South Bank", "postcode": "SE1 9PX", "public": True, "creator": user}
    John_Lyon_Education_Studio = {"name": "John Lyon Education Studio", "address": "The South Bank", "postcode": "SE1 9PX", "public": True, "creator": user}
    Olivier_Theatre = {"name": "Olivier Theatre", "address": "The South Bank", "postcode": "SE1 9PX", "public": True, "creator": user}
    Olivier_Exhibition_Space = {"name": "Olivier Exhibition Space", "address": "The South Bank", "postcode": "SE1 9PX", "public": True, "creator": user}
    National_Theatre = {"name": "National Theatre", "address": "The South Bank", "postcode": "SE1 9PX", "public": True, "creator": user}
    New_London_Theatre = {"name": "New London Theatre", "address": "Drury Lane", "postcode": "WC2B 5PW", "public": True, "creator": user}
    Theatre_Royal_Haymarket  = {"name": "Theatre Royal Haymarket", "address": "18 Suffolk Street", "postcode": "SW1Y 4HT", "public": True, "creator": user}
    Apollo_Theatre = {"name": "Apollo Theatre", "address": "Shaftesbury Avenue", "postcode": "W1D 7ES", "public": True, "creator": user}
    venues = []

    venue_structs = [Cottesloe_Theatre, Lyttelton_Theatre, Djanogly_Concert_Pitch, John_Lyon_Education_Studio]
    venue_structs.extend([New_London_Theatre, Olivier_Theatre, Olivier_Exhibition_Space, Theatre_Royal_Haymarket])
    venue_structs.append(Apollo_Theatre)
    
    for i in venue_structs:
        venue = venue_calculation.submit_venue(**i)[0]

    from_date = date.today()
    to_date = add_months(date(from_date.year, from_date.month, from_date.day), 1)
    query_url_unformatted = "http://www.nationaltheatre.org.uk/calendar/range?from[value][date]=%s&until[value][date]=%s" 
    query_url = query_url_unformatted % (from_date, to_date)
    url = "http://www.nationaltheatre.org.uk"
    f = urllib.urlopen(query_url)
    html = f.read()
    soup = BeautifulSoup(html)
    dates = soup.find_all("div", id="whatson")[0].find_all("h3")
    event_extracts = []
    for i in dates:
        performance_date = extract_text(i.text)[0]
        lis = i.find_next().find_all("li")
        assert(lis)
        for time_row in lis:
            performance_time = get_time(get_one(time_row.find_all("span")).text)
            href = get_one(time_row.find_all("a"))
            link = "%s%s" % (url, href.attrs["href"])
            title = href.text.strip()
            performance_venue = None
            print "venues here with %s" % venues
            for venue in venues:
                print "venue %s" % venue.name
                print "text %s" % time_row.text
                if venue.name in time_row.text:
                    performance_venue = venue
                else:
                    performance_venue = National_Theatre
            event_extracts.append(EventExtract(title, performance_date, "NationalTheatre", user, performance_time, link = link, venue = venue))

    print "saving"
    for i in event_extracts:
        i.save()


