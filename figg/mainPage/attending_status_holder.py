from mainPage.models import AttendingStatus
from figg_calendar import tracking_calculation
from mainPage import tag_calculation

class Attendee(object):
    def __init__(self, user__username, user__id, user__user_details__user_img_normal):
        self.name = user__username
        self.user_id = user__id
        self.img_normal = user__user_details__user_img_normal
        self.selected = False

    def as_json(self):
        return self.__dict__

    def __repr__(self):
        return "%s: %s %s %s %s" % (self.__class__, self.name, self.user_id, self.img_normal, self.selected)

class AttendingStatusHolder(object):
    
    def translate_results(self, results):
        attendees = [Attendee(**x) for x in results]
        return attendees    

    def get_attending(self, event_id, user):
        """returns all people with attending status added or accepted"""
        query = AttendingStatus.objects.filter(event__id = event_id)
        query = query.filter(status__in = [AttendingStatus.ADDED, AttendingStatus.ACCEPTED])
        results = query.values('public', 'user__username', 'user__user_details__user_img_normal', 'user__id')
        attendees = []    

        for result in results:
            if result["public"]:
                attendees.append(Attendee(result["user__username"], result["user__id"], result["user__user_details__user_img_normal"])) 
            else:
                self.privately_added += 1


        if user:
            self.attendees = self.get_selected_users(user, attendees)
        else:
            self.attendees = attendees

    def get_selected_users(self, user, attendees):
        """get all selected"""
        print user.username
        ids = tracking_calculation.get_selected_users(user, [x.user_id for x in attendees])
        print "stelected are %s" % ids

        for x in attendees:
            x.selected = x.user_id in ids

        return attendees

    def get_tags(self, event_id, user):
        tag_names = tag_calculation.get_tags(event_id)
        selected_tag_names = tracking_calculation.get_selected_tags(user, tag_names)
        tags = []

        for tag_name in tag_names:
            tags.append({"name": tag_name, "selected": tag_name in selected_tag_names})

        return tags

    def as_json(self):
        return self.__dict__

    def __init__(self, event_id, user = False):
        self.attendees = []
        self.privately_added = 0
        self.get_attending(event_id, user)
        self.tags = self.get_tags(event_id, user)




