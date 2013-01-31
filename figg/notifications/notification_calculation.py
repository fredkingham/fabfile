from mainPage.event_holder import EventHolderByStatus
from notifications.models import Notification
from notifications.notification_types import InviteNotification, ResponseNotification, NotedNotification, CancelNotification
from notifications import NotificationException
from mainPage.models import AttendingStatus
from mainPage import note_calculation

import logging
logger = logging.getLogger(__name__)

def calculate_shares(query):
    shares = query.values("user_details__user_img_mini", "username")
    result = []
    for share in shares:
        result.append({"sharer": share["username"], "sharer_img": share["user_details__user_img_mini"]})

    if not result:
        return ""

    return result

def get_event_structs(status_ids, user):
    event_holder = EventHolderByStatus(status_ids, user)
    event_holder.populate()
    return event_holder.events[0]

def get_generic_args(notification):
    result = {}
    result["date"] = notification.updated.date()
    result["time"] = notification.updated.time()
    result["notification_id"] = notification.id
    result["notification_type"] = notification.get_notification_type_display()
    #the user is only for the email send so we can strip it out when we move to
    #object 
    result["user"] = notification.user.username
    result["first_name"] = notification.user.first_name
    result["email"] = notification.user.email
    return result

def get_invite(notification):
    ''' if we've been invited but we haven't accepted I want to remove it
    if we've been invited and we have accepted, I just want a plain old
    cancelled to flag up'''
    status = notification.invited_status.from_attending_status
    result = {}
    result['from_user'] = status.user.username
    result['from_user_first_name'] = status.user.first_name

    #toDo privacy option will not always be public....
    result['event'] = get_event_structs([notification.invited_status.to_attending_status.id], notification.user)
    return result

def get_response(notification):
    status = notification.response
    status_response = status.status
    if status_response != AttendingStatus.UNABLE and status_response != AttendingStatus.ACCEPTED:
        raise NotificationException("bad status passed to notifier with %s" % status_response)
    row = {}
    row["accepted"] = status_response == AttendingStatus.ACCEPTED
    row["from_user"] = status.user.username
    row['from_user_first_name'] = status.user.first_name
    row["title"] = status.event.title
    row["event_date"] = status.event.date
    row["img"] = status.event.img
    return row

def get_cancel_information(notification):
    status = notification.response
    row = {}
    row["title"] = status.event_time.event.title
    row["from_user"] = notification.user.username
    row["from_user_first_name"] = notification.user.first_name
    row["event_date"] = status.event_time.date
    row["img"] = status.event_time.event.img
    return row

def get_note_information(notification):
    note = notification.note
    user = notification.user
    row_struct = {}

    if note.deleted:
        return {}

    note_details = note_calculation.calculate_note(note, user)

    event= note.event
    
    if not event:
        raise NotificationException("no event!!")

    statuses = AttendingStatus.objects.filter(user = user, event = event)

    if not len(statuses):
        statuses = AttendingStatus.objects.filter(user = note.creator, event = event)

    if not len(statuses):
        raise NotificationException("unable to find a statuses")

    row_struct['event'] = get_event_structs(statuses, user)


    row_struct['creator'] = note.creator.username
    row_struct['creator_first_name'] = note.creator.first_name
    row_struct['note_id'] = note.id
    row_struct['event_date'] = note.updated
    row_struct['notes'] = note_calculation.notes_from_args(event.id, user)
    return row_struct



def get_notifications(user, from_datetime, last_notification_id = 0):

    notifications = Notification.objects.filter(user = user)
    
    if last_notification_id:
        notifications = notifications.filter(id__lt = last_notification_id)

    notifications = notifications.exclude(notification_type = Notification.CHANGE).order_by("-updated")[:11]

    more  = len(notifications) > 10
    notifications = notifications[:10]

    notification_response = []

    for notification in notifications:
        context = get_notification_context(notification)

        if context:
            notification_response.append(context)

    return {"notifications": notification_response, "more": more}

def get_notification_context(notification):
        row = get_generic_args(notification)
        notification_type = notification.notification_type

        if notification_type == notification.INVITE:
            if notification.invited_status.from_attending_status.deleted:
                return False
            else:
                row = dict(row.items() + get_invite(notification).items())
                result = InviteNotification(**row)

        elif notification_type == notification.RESPONSE:
            status = notification.response
            status_response = status.status

            if status_response != AttendingStatus.UNABLE and status_response != AttendingStatus.ACCEPTED:
                raise NotificationException("bad status passed to notifier %s" % status_response)

            row = dict(row.items() + get_response(notification).items())
            result = ResponseNotification(**row)
        elif notification_type == notification.CANCEL:
            row = dict(row.items() + get_cancel_information(notification).items())
            result = CancelNotification(**row)

        elif notification_type in [notification.MENTION, notification.COMMENT, notification.SHARE]:
            row = dict(row.items() + get_note_information(notification).items())
            result = NotedNotification(**row)

        return result


