import urllib
import os
from django.core.files import File
from django.utils.translation import ugettext as _
from mainPage.models import EventImage


class EventExtractHolder(object):
    def __init__(self, user, events_to_links):
        self.user = user
        self.events_to_links = events_to_links


def get_one(collection):
    assert(len(collection) == 1)
    return collection[0]


def get_and_save_img(img_url):
    result = urllib.urlretrieve(img_url)
    event_img = EventImage()
    event_img.img.save(os.path.basename(img_url), File(open(result[0], 'rb')))
    event_img.save()
    return event_img


def format_title_and_description(u_title, u_description, u_link):
        title = _(u_title[:100])

        if len(title) > 100:
            description = "%s %s. Read More %s" % (
                u_title[100:], u_description, u_link)

            if len(description) > 250:
                description = "%s. Read More %s" % (u_title, u_link)

            if len(description) > 250:
                description = "... Read More %s" % u_link
        else:
            description = "%s. Read More %s" % (u_description, u_link)
            if description > 250:
                description = "Read more %s" % u_link

        description = _(description)

        return (title, description)
