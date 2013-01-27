from hotqueue import HotQueue
from notifications.models import Notification, PostedNotification
from django.conf import settings 

queue = HotQueue(settings.QUEUE_NAME)
NOTIFICATION = PostedNotification.NOTIFICATION

def invite(user, invited_status):
    args = [invited_status.id]
    new_notification = Notification()
    new_notification.notification_type = Notification.INVITE
    new_notification.user = user
    new_notification.invited_status = invited_status
    new_notification.save()
    push(NOTIFICATION, new_notification.id)

def response(user, attending_status):
    #todo add mail templates for attending and push to mail
    new_notification = Notification()
    new_notification.notification_type = Notification.RESPONSE
    new_notification.user = user
    new_notification.response = attending_status
    new_notification.save()
    push(NOTIFICATION, new_notification.id)

def change_time(user, detail_note):
    #todo add mail templates for attending and push to mail
    new_notification = Notification()
    new_notification.notification_type = Notification.CHANGE
    new_notification.user = user
    new_notification.detail_note = detail_note
    new_notification.save()
    push(NOTIFICATION, new_notification.id)

def add_mention(user, note):
    #todo add mail templates for attending and push to mail
    new_notification = Notification()
    new_notification.notification_type = Notification.MENTION
    new_notification.user = user
    new_notification.note = note
    new_notification.save()
    push(NOTIFICATION, new_notification.id)

def add_comment(user, note):
    #todo add mail templates for attending and push to mail
    new_notification = Notification()
    new_notification.notification_type = Notification.COMMENT
    new_notification.user = user
    new_notification.note = note
    new_notification.save()
    push(NOTIFICATION, new_notification.id)

def add_share(user, note):
    new_notification = Notification()
    new_notification.notification_type = Notification.SHARE
    new_notification.user = user
    new_notification.note = note
    new_notification.save()
    push(NOTIFICATION, new_notification.id)

def add_cancel(user, attending_status):
    new_notification = Notification()
    new_notification.notification_type = Notification.CANCEL
    new_notification.user = user
    #the attending status of the creator
    new_notification.response = attending_status
    new_notification.save()
    push(NOTIFICATION, new_notification.id)

def push(obj_type, args):
    queue.put( locals() )


