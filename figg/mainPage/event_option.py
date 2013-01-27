from mainPage.models import AttendingStatus, InvitedStatus
from collections import defaultdict 
from privacy_option import PrivacyOption


class EventOption:

    ADD = "add"
    ADD_PRIVATELY = "add privately"
    ACCEPT = "accept"
    ACCEPT_PRIVATELY = "accept privately"
    UNABLE = "unable"
    REMOVE = "remove"
    INVITE = "invite"
    DISCUSS = "discuss"
    SPAM = "mark as spam"
    CHANGE = "suggest a change"

    

    ALL_OPTIONS = [ADD, ADD_PRIVATELY, ACCEPT, ACCEPT_PRIVATELY, UNABLE]
    ALL_OPTIONS.extend([REMOVE, INVITE, DISCUSS, SPAM])
    OPTIONS = {}
    OPTIONS[ADD] = [ADD, ADD_PRIVATELY]
    OPTIONS[ACCEPT] = [ACCEPT, ACCEPT_PRIVATELY, UNABLE, SPAM]
    OPTIONS[ACCEPT_PRIVATELY] = [ACCEPT_PRIVATELY, UNABLE, SPAM]
    options = []

    def __init__(self, option_type):
        if option_type not in self.ALL_OPTIONS:
            raise "unknown option type"

        self.option_type = option_type
        self.options = self.OPTIONS.get(self.option_type, None)

    @classmethod
    def sorter(self, a, b):
        if not a:
            return 1

        if not b:
            return 0

        opa = a["option_type"]
        opb = b["option_type"]

        return cmp(self.ALL_OPTIONS.index(opa), self.ALL_OPTIONS.index(opb))


def default_user_options():
    return ([], [EventOption.ADD, EventOption.INVITE])

def get_event_options(event_time_id, privacy_option, user):
    '''calculates the users options for a given event time'''
    if privacy_option == PrivacyOption.PRIVATE_BUSY:
        return ([], [])

    options = [EventOption(EventOption.INVITE).__dict__, EventOption(EventOption.DISCUSS).__dict__]

    looking_for = [AttendingStatus.CREATOR, AttendingStatus.ACCEPTED]
    looking_for.extend([AttendingStatus.INVITED, AttendingStatus.ADDED])
    looking_for.extend([AttendingStatus.INVITE, AttendingStatus.UNABLE])

    attending_statuses = AttendingStatus.objects.filter(event_time = event_time_id, user = user)
    attending_statuses = attending_statuses.filter(status__in = looking_for)
    attending_statuses = attending_statuses.values("id", "status")

    all_statuses = [i["status"] for i in attending_statuses]

    statuses = []

    if AttendingStatus.CREATOR in all_statuses:
        statuses.append(AttendingStatus.CREATOR)

    if AttendingStatus.INVITED in all_statuses:
        invited_statuses = [i["id"] for i in attending_statuses if i["status"] == AttendingStatus.INVITED]
        invited_users = get_invited_status_users(invited_statuses)
        statuses.append( "Invited by %s" % ", ".join(invited_users))

        if privacy_option == PrivacyOption.PRIVATE_SHOWN:
            options.append(EventOption(EventOption.ACCEPT_PRIVATELY).__dict__)
        else:
            options.append(EventOption(EventOption.ACCEPT).__dict__)

    if AttendingStatus.ACCEPTED in all_statuses:
        accepted_statuses = [i["id"] for i in attending_statuses if i["status"] == AttendingStatus.ACCEPTED]
        accepted_by = get_invited_status_users(accepted_statuses)
        statuses.append("Accepted invites from %s" % ",".join(accepted_by))
        options.append(EventOption(EventOption.UNABLE).__dict__)

    if not AttendingStatus.ADDED in all_statuses:
        if not AttendingStatus.ACCEPTED in all_statuses:
            if not AttendingStatus.INVITED in all_statuses:
                options.append(EventOption(EventOption.ADD).__dict__)
    elif AttendingStatus.ADDED in all_statuses:
        statuses.append(AttendingStatus.ADDED)
        options.append(EventOption(EventOption.REMOVE).__dict__)

    if options:
        options = sorted(options, EventOption.sorter)

    return (statuses, options)

def get_status_map(event_time_id, users):
    status_to_id = defaultdict(list)
    statuses = AttendingStatus.objects.filter(event_time = event_time_id, user = user)
    statuses = statuses.filter(status__in = looking_for)
    statuses.values("id", "status")

    for status in statuses:
        status_to_id[status["status"]].append(status["id"])

    return status_to_id


def get_invited_status_users(statuses):
    invited = InvitedStatus.objects.filter(to_attending_status__in = statuses)
    return invited.values_list("from_attending_status__user__username", flat = True).distinct()

def get_statuses(event_time_ids, user):
    statuses =  AttendingStatus.objects.filter(event_time__id__in = event_time_ids, user = user).values_list("event_time__id", "status")
    result = defaultdict(list)

    for status in statuses:
        result[status[0]].append(AttendingStatus.ATTENDING_STATUS_CHOICES[status[1]])

    return result


