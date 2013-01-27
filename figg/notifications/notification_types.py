from notifications.models import Notification


class BaseNotification(object):
    def __init__(self, date, time, notification_id, notification_type, user, first_name, email):
        self.date = date
        self.time = time
        self.type = notification_type
        self.id = notification_id
        self.user = user
        self.first_name = first_name
        self.email = email

    def as_json(self):
        return self.__dict__

    def get_template(self):
        return "response"

    def __repr__(self):
        return "%s: %s" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%s: %s" % (self.__class__, self.__dict__)

class CancelNotification(BaseNotification):
    def __init__(self, date, time, notification_id, notification_type, from_user, title, event_date, user, img, first_name, email, from_user_first_name):
        super(CancelNotification, self).__init__(date, time, notification_id, notification_type, user, first_name, email)
        self.from_user = from_user
        self.from_user_first_name = from_user_first_name
        self.title = title
        self.event_date = event_date
        self.img = img

    def msg(self):
        return "%s had cancelled %s" % (self.from_user, self.title)

class InviteNotification(BaseNotification):
    def __init__(self, date, time, notification_id, notification_type, from_user, event, user, first_name, email, from_user_first_name):
        super(InviteNotification, self).__init__(date, time, notification_id, notification_type, user, first_name, email)
        self.from_user = from_user
        self.from_user_first_name = from_user_first_name
        self.event = event

    def msg(self):
        return "you've been invited to '%s' by '%s'" % (self.event.get_title(), self.from_user)

class ResponseNotification(BaseNotification):
    def __init__(self, date, time, notification_id, notification_type, from_user, accepted, title, event_date, img, user, first_name, email, from_user_first_name):
        super(ResponseNotification, self).__init__(date, time, notification_id, notification_type, user, first_name, email)
        self.from_user = from_user
        self.from_user_first_name = from_user_first_name
        self.accepted = accepted
        self.title = title
        self.event_date = event_date
        self.img = img

    def msg(self): 
        if self.accepted:
            return "%s accepted your invite to %s" % (self.user, self.title)
        else:
            return "%s is unable to make %s" % (self.user, self.title)

class NotedNotification(BaseNotification):
    def __init__(self, date, time, notification_id, notification_type, event, notes, creator, note_id, user, event_date, first_name, email, creator_first_name):
        super(NotedNotification, self).__init__(date, time, notification_id, notification_type, user, first_name, email)
        self.event = event
        self.notes = notes
        self.creator = creator
        self.creator_first_name = creator_first_name
        self.note_id = note_id
        self.event_date = event_date

    def msg(self):
        if self.type == Notification.MENTION_LONG:
            return "%s mentioned you in a note for '%s'" % (self.creator, self.event.event_date)
        elif self.type == Notification.COMMENT_LONG:
            return "%s commentted on your note for '%s'" % (self.creator, self.event.event_date)
        else:
            raise "unknown type"

class EarlyNotification(object):
    #can't be bothered to create inheritance tree, notification id is 0
    def __init__(self, event, username, first_name, email, notification_type):
        self.event = event
        self.user = username
        self.first_name = first_name
        self.email = email
        self.type = notification_type

    def msg(self):
        return "Reminder: tomorrow is %s" % self.event.get_title()

    def get_template(self):
        return "response"

