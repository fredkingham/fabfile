from common.user_tag import UserTag
from models import Event as EventDB
from common.cal_holder import CalHolder
from privacy_option import Privacy
from mainPage import event_option, note_calculation, event_option
from mainPage.models import AttendingStatus
import venue_calculation
import HTMLParser
from common import complex_encoder
from django.conf import settings

encoder = complex_encoder.Encoder()


def date_translator(event_date):
    return "s%s" % event_date.strftime("%Y%m%d")


class Event(object):

    def __init__(self, series, public, event_id, description, title, event_date, event_time, venue_id, deleted, time_key, belongs_to_user=False):
        self.cal_holder = CalHolder()

        potential_img = EventDB.objects.get(id=event_id).img

        if potential_img:
            img = potential_img.large_img.url
        else:
            img = "%s%s" % (settings.MEDIA_URL, AttendingStatus.objects.get(event=event_id, status="creator").user.user_details.user_img_bigger)

        self.img = img
        self.event_id = event_id
        self.belongs_to_user = belongs_to_user

        if series:
            self.series = series

        if description:
            self.description = description
        else:
            self.description = None
        self.title = title
        self.event_date = event_date
        self.event_time = event_time
        self.venue_id = venue_id
        self.venue = False
        self.notes = "unset"
        self.options = False
        self.deleted = deleted
        self.statuses = []
        self.time_key = time_key
        self.privacy_option = self.get_privacy_option(
            self.belongs_to_user, public)

    def __hash__(self):
        return hash(self.time_key)

    def __eq__(x, y):
        return x.time_key == y.time_key

    def get_date_key(self):
        return date_translator(self.event_date)

    def add_from(self, user_tags):
        self.cal_holder.extend(user_tags)

    def __repr__(self):
        option = Privacy.LOOK_UP[self.privacy_option]
        return "%s: %s %s %s %s" % (self.__class__, self.event_id, option, self.title, self.event_date)

    def get_date_cont_key(self):
        return "d%s" % self.event_date.strftime("%Y%m%d")

    def set_user(self, user):
        self.user = user

    def add_user_tag(self, user_tag):
        self.cal_holder.append(user_tag)

    def add_user_tags(self, user_tags):
        self.cal_holder.extend(user_tags)

    def get_notes(self):
        if self.notes == "unset":
            self.notes = note_calculation.get_note_count_from_id(
                self.event_id, self.user)

        return self.notes

    def get_title(self):
        if self.privacy_option == Privacy.PRIVATE_BUSY:
            usernames = self.cal_holder.get_cal_usernames()

            if len(usernames) <= 1:
                return "%s is busy" % ", ".join(usernames)
        else:
            h = HTMLParser.HTMLParser()
            return h.unescape(self.title)

    def get_description(self):
        if self.description and self.privacy_option != Privacy.PRIVATE_BUSY:
            return self.description

    def get_time(self):
        if self.event_time:
            return self.event_time.strftime("%I:%M %p").lower().lstrip("0")

        return False

    def get_time_name(self):
        if self.event_time:
            return self.event_time.strftime("t%H%M")
        else:
            return "None"

    def get_venue(self):
        if self.venue_id:
            if not self.venue:
                self.venue = venue_calculation.get_venue_for_id(self.venue_id)
            return self.venue
        else:
            return False

    def get_privacy_option(self, belongs_to_user, public):
        if public:
            return Privacy.PUBLIC
        elif belongs_to_user:
            return Privacy.PRIVATE_SHOWN
        else:
            return Privacy.PRIVATE_BUSY

    def as_struct(self):
        self.cal_holder.get_display_info()
        result = {}
        result["date"] = self.event_date
        result["time"] = self.get_time()
        result["time_name"] = self.get_time_name()
        result["img"] = self.img
        result["public"] = self.privacy_option
        result["title"] = self.get_title()
        result["series"] = getattr(self, "series", None)
        description = self.get_description()

        if description:
            result["description"] = description

        result["noteCount"] = self.get_notes()
        result["id"] = self.event_id
        #we only need unique cal holder details
        result["from"] = self.cal_holder
        result["attending_status"] = self.statuses
        result["venue"] = self.get_venue()
        result["cancelled"] = self.deleted
        result["key"] = self.time_key
        return result

    def as_json(self):
        return self.as_struct()

    def __cmp__(self, other):
        cmp(self.time_key, other.time_key)


class NotLoggedInEvent(Event):

    def get_notes(self):
        return False

    def get_user_options(self):
        return event_option.default_user_options()
