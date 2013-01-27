from mainPage.models import AttendingStatus
from collections import defaultdict
from mainPage.cal_holder import CalHolder
from django.db.models import Q


class PrivacyOption:
    PRIVATE_BUSY = "private busy"
    PRIVATE_SHOWN = "private shown"
    PUBLIC = "public"
    OPTIONS = {PUBLIC: 0, PRIVATE_SHOWN: 1, PRIVATE_BUSY: 2}


# Attending Status methods... 
# we need all attending statuses that refer to this user and these cals
# we really want a map of all distinct detail notes and privacy to attending
# status
class AttendingStatusManager(object):
    '''manages the attending statuses of a user'''

    private_invites = "unset" 
    statuses = "unset"
    user_statuses = "unset"
    private_status = "unset"

    def __init__(self, user, event_time, cal_holder):
        self.user = user
        self.event_time = event_time
        self.cal_holder = cal_holder

    @staticmethod
    def get_not_logged_in_statuses(cal_users, event_time):
        return AttendingStatus.objects.filter(user__in = cal_users, event_time = event_time, public = True, status__in = [AttendingStatus.ADDED, AttendingStatus.ACCEPTED]).values_list("user__username", flat = True)

    def has_been_privately_invited(self, username):

#invited
        invite_responses = [AttendingStatus.INVITED, AttendingStatus.ACCEPTED, AttendingStatus.UNABLE]
        invited_query = AttendingStatus.objects.filter(event_time = self.event_time)
        invited_query = invited_query.filter(status__in = invite_responses, user = self.user)
        invited_query = invited_query.filter(from_invited_status__from_attending_status__user__in = self.cal_holder.get_cal_users())
        invited_query = invited_query.filter(public = False)
        invited_query = invited_query.values_list("from_invited_status__from_attending_status__user__username", flat = True)
        self.private_invites = list(invited_query)

#invites
        invite_query = AttendingStatus.objects.filter(status = AttendingStatus.INVITE, event_time = self.event_time, user = self.user) 
        invite_query = invite_query.filter(to_invited_status__to_attending_status__user__in = self.cal_holder.get_cal_users())
        invite_query = invite_query.filter(to_invited_status__to_attending_status__public = False).values_list("to_invited_status__to_attending_status__user__username", flat = True)
        self.private_invites.extend(list(invite_query))

        return username in self.private_invites

    def get_public_private_status(self, is_private_status_id):

        private_status = {}

        creator = False

        for event_status in self.get_cal_statuses():
            if event_status.user == self.user and event_status.status == AttendingStatus.CREATOR:
                creator = True
            else:
                creator = False

        for event_status in self.get_cal_statuses():
            if not event_status.public:
                if creator or event_status.user == self.user or self.has_been_privately_invited(event_status.user.username):
                    private_status[event_status.id] = PrivacyOption.PRIVATE_SHOWN
                else:
                    private_status[event_status.id] = PrivacyOption.PRIVATE_BUSY
            else:
                private_status[event_status.id] = PrivacyOption.PUBLIC

            self.private_status = private_status


        return self.private_status.get(is_private_status_id, PrivacyOption.PRIVATE_BUSY)

    def load_statuses(self):
        statuses = []
        cals_with_tags = self.cal_holder.cals_with_tags()

        exclude = [AttendingStatus.INVITED, AttendingStatus.UNABLE, AttendingStatus.INVITE]

        for cal, tags in cals_with_tags.items():
            user = self.cal_holder.get_user(cal)
            query = AttendingStatus.objects.filter(user = user, event_time = self.event_time).exclude(status__in = exclude)
            query = query.filter(Q(event_time__event__tags__name__in = tags) | Q(event_time__note__notes__name__in = tags)).distinct()
            statuses.extend(query)

        tags = self.cal_holder.get_tag_only()

        if tags:
            query = AttendingStatus.objects.filter(event_time = self.event_time)
            query.filter(Q(event_time__event__tags__name__in = tags) | Q(event_time__note__notes__name__in = tags)).distinct()
            statuses.extend(query)

        cals = self.cal_holder.get_users(self.cal_holder.get_usernames)

        if cals:
            query = AttendingStatus.objects.filter(user__in = cals, event_time = self.event_time).distinct()
            statuses.extend(query)

        self.statuses = statuses

    def load_user_statuses(self):
        self.user_statuses = AttendingStatus.objects.filter(user = self.user, event_time = self.event_time)

    def get_user_statuses(self):
        self.load_user_statuses()

        for status in self.user_statuses:
            yield status

    def get_cal_statuses(self):

        self.load_statuses()

        for status in self.statuses:
            yield status

    def get_status_map(self):
        status_types = AttendingStatus.COMING_STATUSES
        
        result = defaultdict(list)

        for event_status in self.get_user_statuses():
            if event_status.user == self.user:
                result[event_status.status].append(event_status)

        return result
        
    




