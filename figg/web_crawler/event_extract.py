import urllib, os
from mainPage import event_creator
from django.core.files import File
from django.utils.translation import ugettext as _
from mainPage.models import AttendingStatus, EventImage, Venue

class EventExtract(object):

    def __init__(self, title, date, user, time = None, description = None, link = None, venue = None, img_url = None):
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
        title = _(self.title[:100])

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

        description = _(description)

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







