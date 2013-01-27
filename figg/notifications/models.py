from django.db import models
from datetime import datetime
from mainPage.models import InvitedStatus, Note, AttendingStatus
from django.contrib.auth.models import User

class PostedNotification(models.Model):
    NOTIFICATION = "notification"
    notification_type = models.CharField(max_length = 250)
    args = models.CharField(max_length = 250, null = True)
    processed = models.BooleanField(default = False)
    updated = models.DateTimeField()
    receiver = models.EmailField()

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()
        super(PostedNotification, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: %s %s, %s" % (self.__class__, self.notification_type, self.receiver, self.processed)

    def __repr__(self):
        return "%s: %s %s, %s" % (self.__class__, self.notification_type, self.receiver, self.processed)

class LastCheckedNotification(models.Model):
    user = models.ForeignKey(User, related_name = "last_checked")
    checked = models.DateTimeField()

    def __str__(self):
        return "%s: %s, %s" % (self.__class__, self.user.username, self.checked)

    def __repr__(self):
        return "%s: %s, %s" % (self.__class__, self.user.username, self.checked)

class Notification(models.Model):
    INVITE = 1 #user is invited to an event
    MENTION = 2 #user is mentioned in a note
    COMMENT = 3 #someone the user follows has commented on an event they go to
    RESPONSE = 4 #someone has responded to a users invite
    CHANGE = 5 #someone has suggested a datetime change
    SHARE = 6 #someone has suggested a datetime change
    ACCEPT = 7 #someone has suggested a datetime change
    CANCEL = 8 #someone has cancelled their event

    INVITE_LONG = "invite"
    MENTION_LONG = "mention"
    COMMENT_LONG = "comment"
    RESPONSE_LONG = "response"
    CHANGE_LONG = "change"
    SHARE_LONG = "share"
    ACCEPT_LONG = "accept"
    CANCEL_LONG = "cancel"

    NOTIFICATION_MAP = {
            INVITE: INVITE_LONG,
            MENTION: MENTION_LONG,
            COMMENT: COMMENT_LONG,
            RESPONSE: RESPONSE_LONG,
            CHANGE: CHANGE_LONG,
            SHARE: SHARE_LONG,
            ACCEPT: ACCEPT_LONG,
            CANCEL: CANCEL_LONG
   }

    NOTIFICATION_CHOICES = (
            (INVITE, INVITE_LONG),
            (MENTION, MENTION_LONG),
            (COMMENT, COMMENT_LONG),
            (RESPONSE, RESPONSE_LONG),
            (CHANGE, CHANGE_LONG),
            (SHARE, SHARE_LONG),
            (ACCEPT, ACCEPT_LONG),
            (CANCEL, CANCEL_LONG)
            )

    user = models.ForeignKey(User, related_name = "notification")
    invited_status = models.ForeignKey(InvitedStatus, null = True)
    response = models.ForeignKey(AttendingStatus, null = True)
    note = models.ForeignKey(Note, null = True)
    notification_type = models.IntegerField(choices = NOTIFICATION_CHOICES)
    updated = models.DateTimeField()

    def __str__(self):
        return "%s: %s %s" % (self.__class__, self.get_notification_type_display(), self.updated)

    def __repr__(self):
        return "%s: %s %s" % (self.__class__, self.get_notification_type_display(), self.updated)

    @classmethod
    def get_notification_type(self, choice):
        return self.NOTIFICATION_MAP[choice]

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()
        super(Notification, self).save(*args, **kwargs)


