from django.utils import unittest
from mainPage import event_calculation, note_calculation, event_creator
from notifications import notification_calculation, mail_calculation, early_notifications
from notifications.models import Notification, PostedNotification
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from mainPage.models import InvitedStatus, Event, AttendingStatus, Note
from twitter.models import *
from mainPage.event_option import EventOption
from django.test.client import Client
from common import test_functions
from hotqueue import HotQueue
from django.conf import settings
queue = HotQueue(settings.QUEUE_NAME)

def populate():
    User.objects.create_user('Dave', 'Dave@gmail.com', 'Davepassword')
    User.objects.create_user('Bob', 'Bob@gmail.com', 'Bobpassword')
    User.objects.create_user('Fred', 'Fred@gmail.com', 'Fredpassword')
    default_args = {}
    default_args["description"] = "blah"
    default_args["user_img_mini"] = "blah"
    default_args["user_img_normal"] = "blah"
    default_args["user_img_bigger"] = "blah"

    for name in ["Dave", "Bob", "Fred"]:
        user = User.objects.get(username = name)
        args = default_args.copy()
        args["user"] = user
        user_details = UserDetails(**args)
        user_details.save()

    follower = FollowerLoad(followee = User.objects.get(username = 'Dave'))
    follower.save()
    follower.followers.add(User.objects.get(username = "Fred"))

def get_event_args():
    return  {'description': None, 
            'title': u'something today', 
            'user': User.objects.get(username = "Dave"), 
            'event_date': date(2012, 6, 20),
            'public': True, 
            'invited': set([User.objects.get(username="Bob")])}


def create_test_event(args): 
    event_creator.submit_event(**args)


class NotificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def setup(self):
        test_functions.clean_queue()

    def tearDown(self):
        test_functions.clean_up()

    def queueValidation(self, notification_id):
        test_queue_obj = queue.get()
        self.assertTrue("obj_type" in test_queue_obj)
        self.assertEqual(test_queue_obj["obj_type"], "notification")
        self.assertTrue("args" in test_queue_obj)
        self.assertEqual(test_queue_obj["args"], notification_id)
        next_test_queue_obj = queue.get()
        self.assertIsNone(next_test_queue_obj)

    def testInitialInvite(self):
        create_test_event(get_event_args())
        invited = User.objects.get(username = "Bob")
        invitee = User.objects.get(username = "Dave")
        events = Event.objects.all()
        self.assertEqual(len(events), 1)
        then = datetime(2012, 6, 19)
        db_notifications = Notification.objects.all()
        self.assertEqual(len(db_notifications), 1)
        db_notification = db_notifications[0]
        self.assertEqual(db_notification.user, invited)
        invited_statuses = InvitedStatus.objects.all()
        self.assertEqual(len(invited_statuses), 1)
        self.assertEqual(invited_statuses[0], db_notification.invited_status)
        self.assertIsNone(db_notification.response)
        self.assertIsNone(db_notification.note)
        notifications = notification_calculation.get_notifications(invited, then)
        self.assertEqual(len(notifications["notifications"]), 1)
        self.assertTrue("more" in notifications)
        self.assertFalse(notifications["more"])
        notification = notifications["notifications"][0]
        self.assertEqual(notification.type, Notification.INVITE_LONG)
        self.assertEqual(notification.from_user, "Dave")
        self.assertEqual(notification.id, db_notification.id)
        self.queueValidation(db_notification.id)
        mail_calculation.notify(db_notification.id)
        postedNotifications = PostedNotification.objects.all()
        self.assertEqual(len(postedNotifications), 1)
        postedNotification = postedNotifications[0]
        self.assertEqual(postedNotification.notification_type, PostedNotification.NOTIFICATION)
        #self.assertEqual(postedNotification.receiver, invited.email)
        self.assertEqual(postedNotification.args, str(db_notification.id))
        self.assertTrue(postedNotification.processed)

    def testResponseAccept(self):
        create_test_event(get_event_args())
        invited = User.objects.get(username = "Bob")
        invitee = User.objects.get(username = "Dave")
        then = datetime(2012, 6, 19)
        event_id = Event.objects.all()[0].id

        self.assertEqual(len(Notification.objects.filter(notification_type = Notification.INVITE)), 1)
        invite = Notification.objects.filter(notification_type = Notification.INVITE)[0]
        self.queueValidation(invite.id)

        event_calculation.make_a_change(invited, EventOption.ACCEPT, event_id)
        self.assertEqual(len(Notification.objects.all()), 2)
        self.assertEqual(len(Notification.objects.filter(notification_type = Notification.INVITE)), 1)

        self.assertEqual(len(Notification.objects.filter(notification_type = Notification.RESPONSE)), 1)
        response = Notification.objects.filter(notification_type = Notification.RESPONSE)[0]
        self.assertEqual(response.user, invitee)
        notifications = notification_calculation.get_notifications(invitee, then)
        self.assertEqual(len(notifications["notifications"]), 1)
        self.assertTrue("more" in notifications)
        self.assertFalse(notifications["more"])
        notification = notifications["notifications"][0]
        self.assertEqual(notification.event_date, get_event_args()["event_date"])
        self.queueValidation(notification.id)
        mail_calculation.notify(notification.id)
        postedNotifications = PostedNotification.objects.all()
        self.assertEqual(len(postedNotifications), 1)
        postedNotification = postedNotifications[0]
        self.assertEqual(postedNotification.notification_type, PostedNotification.NOTIFICATION)
        #self.assertEqual(postedNotification.receiver, invitee.email)

    def testResponseUnable(self):
#        self.queue_initialisation()
        create_test_event(get_event_args())
        invited = User.objects.get(username = "Bob")
        invitee = User.objects.get(username = "Dave")
        then = datetime(2012, 6, 19)
        event_id = Event.objects.all()[0].id

        self.assertEqual(len(Notification.objects.filter(notification_type = Notification.INVITE)), 1)
        invite = Notification.objects.filter(notification_type = Notification.INVITE)[0]
        self.queueValidation(invite.id)

        event_calculation.make_a_change(invited, EventOption.UNABLE, event_id)
        self.assertEqual(len(Notification.objects.all()), 2)
        self.assertEqual(len(Notification.objects.filter(notification_type = Notification.INVITE)), 1)
        self.assertEqual(len(Notification.objects.filter(notification_type = Notification.RESPONSE)), 1)
        response = Notification.objects.filter(notification_type = Notification.RESPONSE)[0]
        self.assertEqual(response.user, invitee)
        notifications = notification_calculation.get_notifications(invitee, then)
        self.assertEqual(len(notifications["notifications"]), 1)
        self.assertTrue("more" in notifications)
        self.assertFalse(notifications["more"])
        notification = notifications["notifications"][0]
        self.assertEqual(notification.from_user, invited.username)
        self.assertEqual(notification.user, invitee.username)
        self.queueValidation(response.id)
        mail_calculation.notify(response.id)
        postedNotifications = PostedNotification.objects.all()
        self.assertEqual(len(postedNotifications), 1)
        postedNotification = postedNotifications[0]
        self.assertEqual(postedNotification.notification_type, PostedNotification.NOTIFICATION)
        #self.assertEqual(postedNotification.receiver, invitee.email)

    def testFollowerComment(self):
        args = get_event_args()
        args["invited"] = set()
        create_test_event(args)
        note_maker = User.objects.get(username = "Dave")
        follower = User.objects.get(username = "Fred")
        then = datetime(2012, 6, 19)
        description = "new note"
        event_id = Event.objects.all()[0].id
        event_calculation.make_a_change(follower, EventOption.ADD, event_id)
        note_calculation.create_discuss(description, note_maker, [], event_id)
        self.assertEqual(len(Notification.objects.all()), 1)
        db_notification = Notification.objects.all()[0]
        self.assertEqual(db_notification.user, follower)
        notifications = notification_calculation.get_notifications(User.objects.get(username = "Fred"), then)
        self.assertEqual(len(notifications["notifications"]), 1)
        self.assertTrue("more" in notifications)
        self.assertFalse(notifications["more"])
        notification = notifications["notifications"][0]
        self.assertEqual(notification.type, Notification.COMMENT_LONG)
        self.queueValidation(db_notification.id)
        mail_calculation.notify(db_notification.id)
        postedNotifications = PostedNotification.objects.all()
        self.assertEqual(len(postedNotifications), 1)
        postedNotification = postedNotifications[0]
        self.assertEqual(postedNotification.notification_type, PostedNotification.NOTIFICATION)
        #self.assertEqual(postedNotification.receiver, follower.email)



    def testFollowerMention(self):
        args = get_event_args()
        args["invited"] = set()
        create_test_event(args)
        note_maker = User.objects.get(username = "Bob")
        mentioned = User.objects.get(username = "Fred")
        then = datetime(2012, 6, 19)
        description = "new note @Fred"
        event_obj = Event.objects.all()[0]
        event_id = event_obj.id
        event_calculation.make_a_change(note_maker, EventOption.ADD, event_id)
        note_calculation.create_discuss(description, note_maker, ["Fred"], event_id)
        self.assertEqual(len(Notification.objects.all()), 1)
        db_notification = Notification.objects.all()[0]
        self.assertEqual(db_notification.user, mentioned)
        notifications = notification_calculation.get_notifications(User.objects.get(username = "Fred"), then)
        self.assertEqual(len(notifications["notifications"]), 1)
        self.assertTrue("more" in notifications)
        self.assertFalse(notifications["more"])
        notification = notifications["notifications"][0]
        self.assertTrue(len(Event.objects.all()), 1)
        self.assertEqual(notification.type, Notification.MENTION_LONG)
        self.assertEqual(len(notification.notes), 1)
        self.queueValidation(db_notification.id)
        mail_calculation.notify(db_notification.id)
        postedNotifications = PostedNotification.objects.all()
        self.assertEqual(len(postedNotifications), 1)
        postedNotification = postedNotifications[0]
        self.assertEqual(postedNotification.notification_type, PostedNotification.NOTIFICATION)
        self.assertEqual(postedNotification.receiver, mentioned.email)



    def testInviteFromCancelledInvite(self):
        args = get_event_args()
        create_test_event(args)
        from_user = args["user"]
        to_user = User.objects.get(username = "Bob")

        self.assertEqual(len(Event.objects.all()), 1)
        event_time = Event.objects.all()[0]
        event_calculation.cancel_event(event_time.id, from_user)
        notifications = notification_calculation.get_notifications(to_user, date.today())
        self.assertEqual(len(notifications["notifications"]), 0)
        self.assertTrue("more" in notifications)
        self.assertFalse(notifications["more"])
        postedNotifications = PostedNotification.objects.all()
        self.assertEqual(len(postedNotifications), 0)

#    def testAcceptedInviteFromCancelledInvite(self):
#        args = get_event_args()
#        create_test_event(args)
#        from_user = args["user"]
#        to_user = User.objects.get(username = "Bob")
#
#        self.assertEqual(len(EventTime.objects.all()), 1)
#        event_time = EventTime.objects.all()[0]
#        event_calculation.accept(to_user, EventOption.ACCEPT, event_time)
#        event_calculation.cancel_event(event_time.id, from_user)
#        db_notifications = Notification.objects.filter(user = from_user)
#        self.assertEqual(len(db_notifications), 1)
#        notifications = notification_calculation.get_notifications(to_user, date.today())
#        self.assertEqual(len(notifications), 1)

    def test_early_notification(self):
        args = get_event_args()
        tomorrow = date.today() + timedelta(1)
        args["event_date"] = tomorrow
        print "args %s" % args
        create_test_event(args)
        early_notifications.send_early_notifications()
        self.assertEqual(1, 1)

class NotificationViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def testReadAllNotifications(self):
        c = Client()
        logged_in  = c.login(username = 'Dave', password = 'Davepassword')
        result = c.post('/!read_notification/', {'forDate': 20120910})
        self.assertEqual(result.content, "[]")



#    def testChangeTime(self):
#        args = get_event_args()
#        args["invited"] = set()
#        create_test_event(args)
#        detail_maker = User.objects.get(username = "Dave")
#        notifiee = User.objects.get(username = "Fred")
#        then = datetime(2012, 6, 19)
#        event_id = EventTime.objects.all()[0].id
#        event_date = "30 Aug 2012"
#        description = "whatevs"
#        event_calculation.make_a_change(notifiee, EventOption.ADD, event_id)
#        note_calculation.create_detail(event_date, None, description, detail_maker, [], event_id)
#        self.assertEqual(len(DetailNote.objects.all()), 1)
#        db_notifications = Notification.objects.all()
#        self.assertEqual(len(Notification.objects.all()), 1)
#        db_notification = Notification.objects.all()[0]
#        self.assertEqual(db_notification.user, notifiee)
#        notifications = notification_calculation.get_notifications(User.objects.get(username = "Fred"), then)
#        self.assertEqual(len(notifications), 1)
#        notification = notifications[0]
#        for i in ["updated", "date_title", "date_key", "time", "time_key", "type"]:
#            self.assertTrue(i in notification)




