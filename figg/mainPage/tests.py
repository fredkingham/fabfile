from django.test import TestCase
from django.test.client import Client
from mainPage import event_calculation, event_key, event_creator, preview_calculation
from mainPage.models import *
from figg_calendar.models import TrackingCal
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from mainPage.privacy_option import PrivacyOption
from mainPage.event_holder import EventHolderForUser
from mainPage import event_holder

from django.utils import simplejson
from common import test_functions 
from mainPage.attending_status_holder import AttendingStatusHolder
from preview_calculation import Regularity
from common.figgDate import FiggDate


class EventKeyTest(TestCase):
    def test_key(self):
        previous_date = date.today() + timedelta(-1)
        previous_time = time(0, 0)
        previous_key = event_key.create_date_key(previous_date, previous_time)
        for i in xrange(10):
            new_date = date.today() + timedelta(i)
            for y in xrange(24):
                for z in xrange(59):
                    new_time = time(y, z + 1)
                    new_key = event_key.create_date_key(new_date, new_time)
                    self.assertTrue(new_key > previous_key, "print new key is %s old key is %s" % (new_key, previous_key))
                    self.assertEqual(len(str(new_key)), 18)
                    previous_key = new_key


class PreviewCalculation(TestCase):
    """PreviewCalculation tests for regularity daily/weekly/monthly"""
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def tearDown(self):
        test_functions.clean_up()

    def setUp(self):
        c = self.client
        c.login(username='Dave', password='Davepassword')

    def test_daily_calc(self):
        repeat_regularity = Regularity.DAILY
        event_date = date.today()
        delta = timedelta(1)
        repeat_until = event_date + delta
        event_time = None
        result = preview_calculation.times_calculation(
            repeat_regularity, event_date, event_time, repeat_until)
        self.assertEqual(len(result), 2)
        today = FiggDate(date.today())
        self.assertIn(today, result)
        self.assertIn(FiggDate(repeat_until), result)

    def test_daily_calc_over_month_end(self):
        repeat_regularity = Regularity.DAILY
        event_date = date(2012, 10, 31)
        delta = timedelta(7)
        repeat_until = event_date + delta
        event_time = None
        result = preview_calculation.times_calculation(
            repeat_regularity, event_date, event_time, repeat_until)
        self.assertEqual(len(result), 8)

        for i in xrange(7):
            the_date = event_date + timedelta(i)
            self.assertIn(FiggDate(the_date), result)

    def test_weekly_calc_one(self):
        repeat_regularity = Regularity.WEEKLY
        event_date = date.today()
        delta = timedelta(1)
        repeat_until = event_date + delta
        event_time = None
        result = preview_calculation.times_calculation(
            repeat_regularity, event_date, event_time, repeat_until)
        self.assertEqual(len(result), 1)
        today = FiggDate(date.today())
        self.assertIn(today, result)

    def test_weekly_calc(self):
        repeat_regularity = Regularity.WEEKLY
        event_date = date.today()
        delta = timedelta(7)
        repeat_until = event_date + delta
        event_time = None
        result = preview_calculation.times_calculation(
            repeat_regularity, event_date, event_time, repeat_until)
        self.assertEqual(len(result), 2)
        today = FiggDate(date.today())
        self.assertIn(today, result)
        self.assertIn(FiggDate(repeat_until), result)

    def test_weekly_over_month(self):
        repeat_regularity = Regularity.WEEKLY
        event_date = date(2012, 10, 31)
        delta = timedelta(33)
        repeat_until = event_date + delta
        event_time = None
        result = preview_calculation.times_calculation(
            repeat_regularity, event_date, event_time, repeat_until)
        self.assertEqual(len(result), 5)

        for i in xrange(33, 7):
            the_date = event_date + timedelta(i)
            self.assertIn(FiggDate(the_date), result)


class ViewTest(TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def setUp(self):
        c = self.client
        c.login(username='Dave', password='Davepassword')

    def get_event_args(self):
        user = User.objects.get(username="Dave")
        event_args = {
            'description': None,
            'title': u'something today',
            'user': user,
            'event_date': date(2012, 6, 20),
            'event_time': None,
            'public': True,
            'invited': ''
        }
                #'invited': set([])}
        return event_args.copy()

    def tearDown(self):
        test_functions.clean_up()

    def test_get_dateline(self):
        c = self.client
        result = c.get('/!get_dateline/', {'start_date': 20120910})
        self.assertEqual(result.content, '{}')

    def test_get_dateline_for_date(self):
        c = self.client
        args = {'startDate': 20120901, 'end_date': 20121001}
        result = c.get('/!get_dateline/', args)
        self.assertEqual(result.content, '{}')

    def test_long_event_creator(self):
        args = {
            "title": "some event this is going to be massive it's happening today which is nice you know so there",
            "event_date": 20130102,
            "public": True
        }

        c = self.client
        json_response = c.post('/!event_creator_from_json/', args)
        response = simplejson.loads(json_response.content)
        self.assertEqual(response, 0)
        self.assertEqual(len(Event.objects.all()), 1)

    def test_page_details(self):
        c = self.client
        response = c.get('/Dave')
        page_details = response.context["page_details"]
        self.assertEqual(page_details["cal"], "Dave")

        event_args = test_functions.get_event_args()
        event_args["description"] = "#hello"
        test_functions.create_event(event_args)

        response = c.get('/t/hello')
        page_details = response.context["page_details"]
        self.assertEqual(page_details["start_date"], date.today())
        self.assertEqual(page_details["tag"], "hello")

    def test_note_tag_search(self):
        """ tests the whole flow for the create a note, search by the note, get
        notes"""
        c = self.client
        test_functions.create_event()
        self.assertFalse(Tag.objects.all().exists())
        event_id = Event.objects.all()[0].id
        args = {}
        args["description"] = "a #tag"
        args["eventId"] = event_id
        c.post("/!discuss_creator/", args)
        self.assertEqual(len(Tag.objects.all()), 1)
        tag = Tag.objects.all()[0]
        tag.description = "a #tag"
        self.assertEqual(len(tag.events.all()), 1)
        self.assertEqual(tag.events.all()[0].id, event_id)
        args = {"tag": "tag", "start_date": 20120620}
        json_response = c.get('/!get_all_events', args)
        print "json response %s" % json_response
        response = simplejson.loads(json_response.content)
        self.assertEqual(len(response["events"]), 1)

    def test_search_term(self):
        c = self.client
        json_response = c.get('/!search_term/', {'start_date':
                              20120910, 'search_term': 'blah'})
        response = simplejson.loads(json_response.content)
        self.assertIn("more", response)
        self.assertFalse(response["more"])
        self.assertIn("events", response)
        self.assertEqual(len(response["events"]), 0)

    def test_event_cancel(self):
        event_args = test_functions.get_event_args()
        event_creator.submit_event(**event_args)
        self.assertEqual(len(Event.objects.all()), 1)
        event_time = Event.objects.all()[0]
        user = event_args["user"]
        event_calculation.cancel_event(event_time.id, user)
        self.assertEqual(len(Event.objects.all()), 1)
        event_time = Event.objects.all()[0]
        self.assertTrue(event_time.deleted)

    def test_event_edit(self):
        test_functions.create_event()
        print "creator %s" % AttendingStatus.objects.filter(
            status=AttendingStatus.CREATOR)
        change_args = {
            'title': '@fredkingham something tomorrow should be good',
            'who': ['fredkingham'],
            'event_date': '20120917',
            'event_time': None,
            'description': '',
            'public': False
        }
        change_args["event"] = Event.objects.all()[0].id
        event_args = test_functions.get_event_args()

        c = self.client
        response = c.post('/!event_editor/', data=change_args)
        self.assertEqual(response.content, '1')
        self.assertEqual(len(Event.objects.all()), 1)
        response = c.post('/!event_editor/', data=change_args)
        self.assertEqual(response.content, '1')
        self.assertEqual(len(Event.objects.all()), 1)
        same_event_obj = Event.objects.all()[0]
        self.assertEqual(event_args["title"], same_event_obj.title)
        self.assertEqual(event_args["description"], same_event_obj.description)
        self.assertEqual(date(2012, 6, 20), same_event_obj.date)

        d = Client()
        d.login(username='fredkingham', password='Fredpassword')
        response = d.post('/!event_editor/', data=change_args)
        self.assertEqual(response.content, '0')
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.title, change_args["title"])
        self.assertEqual(event.description, None)
        self.assertEqual(event.date, date(2012, 9, 17))

    def test_get_all_events(self):
        c = self.client
        args = {"start_date": 20121010}
        json_response = c.get('/!get_all_events', args)
        response = simplejson.loads(json_response.content)
        self.assertFalse(response["more"], False)
        self.assertFalse(response["events"], [])

        args = test_functions.get_event_args()
        args["description"] = "#hello"
        test_functions.create_event(args)
        # nothing at this start date
        json_response = c.get(
            '/!get_all_events', {'tag': "hello", "start_date": 20121010})
        response = simplejson.loads(json_response.content)
        self.assertFalse(response["more"], False)
        self.assertFalse(response["events"], [])

        #event is in the past so nothing is returned
        json_response = c.get(
            '/!get_all_events', {'tag': "hello", "end_date": 19901010})
        response = simplejson.loads(json_response.content)
        self.assertTrue(response["more"])
        self.assertFalse(response["events"], [])

        json_response = c.get(
            '/!get_all_events', {'tag': "hello", "end_date": 20121010})
        response = simplejson.loads(json_response.content)
        self.assertFalse(response["more"], False)
        self.assertEqual(len(response["events"]), 1)

    def test_get_all_events_with_cancelled(self):
        c = self.client
        test_functions.create_event()
        event = Event.objects.all()[0]
        user = AttendingStatus.objects.get(
            event=event, status=AttendingStatus.CREATOR).user
        event_id = event.id
        event_date = event.date.strftime("%Y%m%d")
        event_calculation.cancel_event(event_id, user)
        self.assertTrue(Event.objects.filter(deleted=True).exists())
        self.assertFalse(Event.objects.filter(deleted=False).exists())
        event_date = event.date.strftime("%Y%m%d")
        json_response = c.get(
            '/!get_all_events', {"start_date": event_date}).content
        response = simplejson.loads(json_response)
        self.assertFalse(response["previous"])
        self.assertFalse(response["more"])
        self.assertEqual(len(response["events"]), 0)

    def test_get_all_events_with_more(self):
        args = test_functions.get_event_args()
        args["event_date"] = date.today()
        c = self.client

        for i in xrange(event_holder.DEFAULT_CAP + 1):
            test_functions.create_event(args)

        args = {"start_date": 20121010}
        json_response = c.get('/!get_all_events', args)
        response = simplejson.loads(json_response.content)
        self.assertTrue(response["more"])
        self.assertEqual(len(response["events"]), event_holder.DEFAULT_CAP)

    def test_not_logged_in_get_all_events_tag(self):
        c = self.client
        args = {'tag': 'hello', 'start_date': 20121004}
        json_response = c.get('/!get_all_events', args)
        response = simplejson.loads(json_response.content)
        self.assertFalse(response["more"], False)
        self.assertFalse(response["events"], [])

    def test_not_logged_in_get_all_events_cal(self):
        c = self.client
        args = {"cal": "fredkingham", "start_date": 20121004}
        json_response = c.get('/!get_all_events', args)
        response = simplejson.loads(json_response.content)
        self.assertFalse(response["more"], False)
        self.assertFalse(response["events"], [])


class ViewTestEventCreating(TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def tearDown(self):
        test_functions.clean_up()

    def setUp(self):
        c = self.client
        c.login(username='Dave', password='Davepassword')

    def test_create_event(self):
        c = self.client
        self.assertEqual(len(Event.objects.all()), 0)
        args = {}
        args["title"] = "something today"
        args["description"] = ""
        args["event_date"] = "20121004"
        args["event_time"] = "null"
        args["public"] = True
        json_response = c.post('/!event_creator_from_json/', args)
        response = simplejson.loads(json_response.content)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.date, date(2012, 10, 4))
        self.assertEqual(event.title, "something today")
        self.assertEqual(event.description, None)
        self.assertEqual(event.public, True)

    def test_create_event_private(self):
        c = self.client
        self.assertEqual(len(Event.objects.all()), 0)
        args = {}
        args["title"] = "something today"
        args["description"] = ""
        args["event_date"] = "20121004"
        args["event_time"] = "null"
        args["public"] = False
        json_response = c.post('/!event_creator_from_json/', args)
        response = simplejson.loads(json_response.content)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.date, date(2012, 10, 4))
        self.assertEqual(event.title, "something today")
        self.assertEqual(event.description, None)
        self.assertEqual(event.public, False)

    def test_create_event_with_venue(self):
        c = self.client
        venue = test_functions.create_venue()
        self.assertEqual(len(Event.objects.all()), 0)
        args = {}
        args["title"] = "something today"
        args["description"] = ""
        args["event_date"] = "20121004"
        args["event_time"] = "null"
        args["event_venue"] = venue.id
        args["public"] = True
        json_response = c.post('/!event_creator_from_json/', args)
        response = simplejson.loads(json_response.content)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.date, date(2012, 10, 4))
        self.assertEqual(event.title, "something today")
        self.assertEqual(event.description, None)
        self.assertEqual(event.venue, venue)

    def test_create_event_with_invited(self):
        c = self.client
        self.assertEqual(len(Event.objects.all()), 0)
        args = {}
        args["title"] = "something today"
        args["description"] = ""
        args["event_date"] = "20121004"
        args["event_time"] = "null"
        args["public"] = True
        args["invited"] = "Dave,Fred"
        json_response = c.post('/!event_creator_from_json/', args)
        response = simplejson.loads(json_response.content)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.date, date(2012, 10, 4))
        self.assertEqual(event.title, "something today")
        self.assertEqual(event.description, None)
        self.assertEqual(len(InvitedStatus.objects.all()), 2)

    def test_create_event_with_repeating(self):
        c = self.client
        self.assertEqual(len(Event.objects.all()), 0)
        args = {}
        args["description"] = u''
        args["event_time"] = u'null'
        args["title"] = u'today is nice'
        args["invited"] = u''
        args["repeat_regularity"] = u'DAILY'
        args["repeat_until"] = u'Fri Dec 14 2012 00:00:00 GMT+0000 (GMT)'
        args["event_date"] = "20121212",
        args["public"] = u'true'
        json_response = c.post('/!event_creator_from_json/', args)
        response = simplejson.loads(json_response.content)
        self.assertEqual(len(Event.objects.all()), 3)


class EventValidation(TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def setUp(self):
        c = self.client
        c.login(username='Dave', password='Davepassword')

    def test_long_title(self):
        """ not a great test but just make sure it blows up """
        event_args = test_functions.get_event_args()
        event_creator.submit_event(**event_args)

        title = """this is a very long tweet that invites @Bob, I'm hoping he
        really appreciates it, as we want to do something tomorrow and this is
        nice"""

        change_args = {
            'title': title,
            'who': ['fredkingham'],
            'eventDate': 'Mon Sep 17 2012 01:00:00 GMT+0100 (BST)',
            'eventTime': None,
            'public': False
        }

        c = self.client
        response = c.post('/!event_editor/', data=change_args)
        self.assertEqual(response.content, '1')


class EventCalculationTest(TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def get_args(self):
        args = {'user': User.objects.get(username='fredkingham'),
                'repeat_until': None,
                'description': None,
                'title': u'create a private event today',
                'event_date': date(2012, 6, 20),
                'repeat_regularity': None,
                #'invited': set([]),
                'invited': '',
                'public': True,
                'event_venue': None}

        return args

    def test_create_events(self):
        args = {'description': None,
                'title': u'something today',
                'user': User.objects.get(username="fredkingham"),
                'event_date': date(2012, 6, 20),
                'event_time': None,
                'public': True,
                'invited': ''
                #'invited': set([])}
                }

        event_creator.submit_event(**args)
        self.assertEqual(len(Event.objects.all()), 1)

    def test_submit_event(self):
        args = self.get_args()
        event_creator.submit_event(**args)
        self.assertEqual(len(Event.objects.all()), 1)
        user = args["user"]
        self.assertEqual(len(AttendingStatus.objects.exclude(user=user)), 0)

    def test_submit_and_read_private(self):
        args = self.get_args()
        args["public"] = False

        event_creator.submit_event(**args)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertFalse(event.public)
        start_date = date(2012, 6, 20)

        user = User.objects.get(username="fredkingham")
        TrackingCal.objects.create(user=user, cal=user)
        event_holder = EventHolderForUser(start_date=start_date, user=user)
        event_holder.populate()
        events = event_holder.events
        self.assertEqual(len(events), 1)
        event = events[0]
        privacy = PrivacyOption.OPTIONS[PrivacyOption.PRIVATE_SHOWN]
        self.assertEqual(event.get_privacy_option(True, False), privacy)
        self.assertEqual(len(event.statuses), 2)
        self.assertTrue(AttendingStatus.ADDED_SHORT in event.statuses)
        self.assertTrue(AttendingStatus.CREATOR_SHORT in event.statuses)
        self.assertFalse(
            AttendingStatus.ADDED_SHORT == AttendingStatus.CREATOR_SHORT)

    def get_generic_event_args(self):
        return {'user': User.objects.get(username='fredkingham'),
                'repeat_until': None,
                'description': None,
                'title': u'A truly random name blah',
                'event_date': date(2012, 7, 1),
                'repeat_regularity': None,
                'public': True,
                'event_venue': None}

    def generic_event_create(self):
        args = self.get_generic_event_args()
        event_creator.submit_event(**args)

    def test_submit_generic_event(self):
        self.generic_event_create()
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.date, date(2012, 7, 1))
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.title, "A truly random name blah")
        self.assertEqual(event.description, None)
        self.assertEqual(len(AttendingStatus.objects.all()), 2)
        user = User.objects.get(username="fredkingham")
        creator = AttendingStatus.CREATOR
        added = AttendingStatus.ADDED
        self.assertEqual(len(AttendingStatus.objects.filter(
                             user=user, status=creator)), 1)
        self.assertEqual(len(AttendingStatus.objects.filter(
                             user=user, status=added)), 1)

    def cancel_event(self):
        self.generic_event_create()
        event_id = Event.objects.all()[0].id
        user = User.objects.get(username="fredkingham")
        event_calculation.cancel_event(user, event_id)
        self.assertEqual(Event.objects.all(), 1)
        event = Event.objects.all()[0]
        self.assertTrue(event.deleted)
        self.assertTrue(len(AttendingStatus.objects.all()), 1)
        attending_status = AttendingStatus.objects.all()[0]
        self.assertEqual(attending_status.status, AttendingStatus.CREATOR)

    def test_edit_event_time(self):
        self.generic_event_create()
        args = self.get_generic_event_args()
        args["event"] = Event.objects.all()[0]
        del args["repeat_regularity"]
        del args["repeat_until"]
        wrong_user = User.objects.get(username="Dave")
        args["user"] = wrong_user
        self.assertFalse(event_calculation.edit_event(**args))
        args["user"] = User.objects.get(username="fredkingham")
        args["event_date"] = date(2012, 8, 1)
        self.assertTrue(event_calculation.edit_event(**args))
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(args["event"], event)
        self.assertEqual(date(2012, 8, 1), event.date)
        self.assertEqual(event.time, None)
        self.assertEqual(args["description"], event.description)
        self.assertEqual(args["title"], event.title)

    def test_edit_event(self):
        self.generic_event_create()
        args = self.get_generic_event_args()
        args["event"] = Event.objects.all()[0]
        del args["repeat_regularity"]
        del args["repeat_until"]
        args["title"] = "a whole new title"
        self.assertTrue(event_calculation.edit_event(**args))
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(args["event_date"], event.date)
        self.assertEqual(None, event.time)
        self.assertEqual(event.description, None)
        self.assertEqual(event.title, "a whole new title")

    def test_invite_note(self):
        args = self.get_args()
        event_creator.submit_event(**args)
        note_args = {}
        note_args["description"] = "@figg_sport do you fancy this?"

    def tearDown(self):
        Event.objects.all().delete()
        AttendingStatus.objects.all().delete()


class AttendingTest(TestCase):
    """ test that the event display is as expected with all the relevent
    info and with the href's properly displayed"""

    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def tearDown(self):
        test_functions.clean_up()

    def test_basic_attendee(self):
        test_functions.create_event()
        self.assertEqual(len(Event.objects.all()), 1)
        self.assertEqual(len(AttendingStatus.objects.all()), 2)
        a = Event.objects.all()[0].id
        status_holder = AttendingStatusHolder(a)
        self.assertEqual(len(status_holder.attendees), 1)
        self.assertEqual(status_holder.privately_added, 0)

    def test_private_attendee(self):
        args = test_functions.get_event_args()
        args["public"] = False
        event_creator.submit_event(**args)
        self.assertEqual(len(Event.objects.all()), 1)
        self.assertEqual(len(AttendingStatus.objects.all()), 2)
        a = Event.objects.all()[0].id
        status_holder = AttendingStatusHolder(a)
        self.assertEqual(len(status_holder.attendees), 0)
        self.assertEqual(status_holder.privately_added, 1)

    def test_view(self):
        c = self.client
        test_functions.create_event()
        event_id = Event.objects.all()[0].id
        args = {"id": event_id}
        json_response = c.get("/!get_attending", args)
        response = simplejson.loads(json_response.content)
        self.assertEqual(len(response["attendees"]), 1)
        self.assertEqual(response["privately_added"], 0)

    def test_attend_event_get_all_events(self):
        test_functions.create_event(
            {"user": User.objects.get(username="fredkingham")})
        self.assertFalse(AttendingStatus.objects.filter(
                         user__username="Dave").exists())
        event = Event.objects.all()[0]
        event_id = event.id
        user = User.objects.get(username="Dave")
        event_calculation.make_a_change(user, "add", event_id)
        status = AttendingStatus.objects.get(user__username="Dave")
        self.assertEqual(status.event, event)


class EventDisplayTest(TestCase):
    """ test that the event display is as expected with all the relevent
    info and with the href's properly displayed"""

    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def setUp(self):
        c = self.client
        c.login(username='Dave', password='Davepassword')

    def tearDown(self):
        test_functions.clean_up()

    def json_args(self):
        tomorrow = date.today() + timedelta(1)
        title = "something tomorrow"
        description = "because you know"
        event_date = "20121010"  # tomorrow.strftime("%Y%m%d")
        event_time = None
        public = True
        return locals()

    def test_without_description(self):
        event_args = self.json_args()
        event_args = self.json_args()
        del(event_args["description"])
        c = self.client
        response = c.post('/!event_creator_from_html/', data=event_args)
        event = Event.objects.all()[0]
        self.assertEqual(event.title, event_args["title"])

    def test_with_script_tag(self):
        event_args = self.json_args()
        event_args["description"] = "<script>alert('hello')</script>"
        c = self.client
        response = c.post('/!event_creator_from_html/', data=event_args)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.title, event_args["title"])
        description = event.description
        self.assertNotEqual(description, event_args["description"])

    def test_escaping(self):
        event_args = self.json_args()
        event_args["description"] = "The dog's on fire"
        c = self.client
        response = c.post('/!event_creator_from_html/', data=event_args)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.title, event_args["title"])
        description = event.description
        self.assertEqual(event_args["description"], event.description)
