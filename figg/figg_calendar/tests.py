from common import test_functions
from django.utils import simplejson
from django.test import TestCase
from figg_calendar import tracking_calculation
from django.contrib.auth.models import User
from figg_calendar.models import *


class SignalTest(TestCase):

    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def tearDown(self):
        test_functions.clean_up()

    def test_create_defaults(self):
        self.assertFalse(TrackingCal.objects.all())
        self.assertFalse(TrackingTag.objects.all())
        user = User.objects.get(username="fredkingham")
        test_functions.create_tag()
        tracking_calculation.populate_defaults(user)
        self.assertTrue(TrackingCal.objects.filter(user=user))
        self.assertTrue(TrackingTag.objects.all())

    def testSignalFired(self):
        self.assertFalse(TrackingCal.objects.all())
        test_functions.create_tag()
        User.objects.create_user('Dave_Test', 'Dave_Test@gmail.com', 'Davepassword')
        self.assertTrue(TrackingCal.objects.all())
        self.assertTrue(TrackingTag.objects.all())


class TrackingCalculationTest(TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def tearDown(self):
        test_functions.clean_up()

    def test_select_cal(self):
        """ create a calendar, deselect a calendar, reselect a calendar, remove a calendar """
        self.assertFalse(TrackingCal.objects.all())
        user = User.objects.get(username="fredkingham")
        dave = User.objects.get(username="Dave")
        cal_id = dave.id
        tracking_calculation.select(user, True, cal=dave)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        following = TrackingCal.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.cal, User.objects.get(id=cal_id))
        self.assertTrue(following.selected)

        # adding it again, should just remain selected
        tracking_calculation.select(user, True, cal=dave)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        following = TrackingCal.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.cal, dave)
        self.assertTrue(following.selected)

        # deselecting
        tracking_calculation.select(user, False, cal=dave)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        following = TrackingCal.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.cal, dave)
        self.assertFalse(following.selected)

        #reselect
        tracking_calculation.select(user, True, cal=dave)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        following = TrackingCal.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.cal, dave)
        self.assertTrue(following.selected)

        #remove
        tracking_calculation.remove(user, cal=dave)
        self.assertEqual(len(TrackingCal.objects.all()), 0)

        # adding it again, should just remain selected
        tracking_calculation.select(user, True, cal=dave)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        following=TrackingCal.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.cal, dave)
        self.assertTrue(following.selected)

    def test_select_tag(self):
        """ create a calendar, deselect a calendar, reselect a calendar, remove a calendar """
        self.assertFalse(Tag.objects.all())
        test_functions.create_tag()
        self.assertFalse(TrackingTag.objects.all())
        user = User.objects.get(username="fredkingham")
        tag = Tag.objects.get(name = "hello")
        tracking_calculation.select(user, True, tag=tag)
        self.assertEqual(len(TrackingTag.objects.all()), 1)
        following = TrackingTag.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.tag, tag)
        self.assertTrue(following.selected)

        # adding it again, should just remain selected
        tracking_calculation.select(user, True, tag=tag)
        self.assertEqual(len(TrackingTag.objects.all()), 1)
        following = TrackingTag.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.tag, tag)
        self.assertTrue(following.selected)

        # deselecting
        tracking_calculation.select(user, False, tag=tag)
        self.assertEqual(len(TrackingTag.objects.all()), 1)
        self.assertEqual(len(TrackingCal.objects.all()), 0)
        self.assertEqual(len(TrackingSeries.objects.all()), 0)
        self.assertEqual(len(TrackingVenue.objects.all()), 0)
        following=TrackingTag.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.tag, tag)
        self.assertFalse(following.selected)

        #reselect
        tracking_calculation.select(user, True, tag=tag)
        self.assertEqual(len(TrackingTag.objects.all()), 1)
        self.assertEqual(len(TrackingCal.objects.all()), 0)
        self.assertEqual(len(TrackingSeries.objects.all()), 0)
        self.assertEqual(len(TrackingVenue.objects.all()), 0)
        following=TrackingTag.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.tag, tag)
        self.assertTrue(following.selected)

        #remove
        tracking_calculation.remove(user, tag=tag)
        self.assertEqual(len(TrackingTag.objects.all()), 0)

        # adding it again, should just remain selected
        tracking_calculation.select(user, True, tag=tag)
        self.assertEqual(len(TrackingTag.objects.all()), 1)
        following=TrackingTag.objects.all()[0]
        self.assertEqual(following.user, user)
        self.assertEqual(following.tag, tag)
        self.assertTrue(following.selected)

    def test_get_tracking(self):
        user=User.objects.get(username="fredkingham")
        result=tracking_calculation.get_tracking(user, user)
        empty = {'series': [], 'cal': [], 'venue': [], 'tag': [], 'title': "You're tracking"}
        self.assertEqual(result, empty)
        dave=User.objects.get(username="Dave")
        tracking_calculation.select(user, True, cal=dave)
        result=tracking_calculation.get_tracking(user, user)
        trackee = result["cal"][0]
        self.assertEqual(trackee.name, "Dave")
        self.assertEqual(trackee.img_normal, "blah")
        self.assertEqual(trackee.selected, True)

        test_functions.create_tag()
        tag=Tag.objects.get(name = "hello")
        tracking_calculation.select(user, True, tag=tag)
        result=tracking_calculation.get_tracking(user, user)
        tag_results = result["tag"]
        self.assertEqual(len(tag_results), 1)
        self.assertEqual(tag_results[0].name, "hello")
        self.assertEqual(tag_results[0].selected, True)


class SelectViewTest(TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    def setUp(self):
        c = self.client
        c.login(username='Dave', password='Davepassword')

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def tearDown(self):
        test_functions.clean_up()

    def test_select_calendar(self):
        self.assertFalse(TrackingCal.objects.all())
        cal = User.objects.get(username="fredkingham")
        args = {"cal": cal.id, "add": True}
        json_result = self.client.post('/f/tracking/select', args)
        result = simplejson.loads(json_result.content)
        self.assertEqual(result, 0)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        tracking = TrackingCal.objects.all()[0]
        self.assertEqual(tracking.user, User.objects.get(username="Dave"))
        self.assertEqual(tracking.cal, cal)
        self.assertEqual(tracking.selected, True)

    def test_select_calendar_add_and_deselect(self):
        self.assertFalse(TrackingCal.objects.all())
        cal = User.objects.get(username="fredkingham")
        args = {"cal": cal.id, "add": True}
        json_result = self.client.post('/f/tracking/select', args)
        result = simplejson.loads(json_result.content)
        self.assertEqual(result, 0)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        tracking = TrackingCal.objects.all()[0]
        self.assertEqual(tracking.user, User.objects.get(username="Dave"))
        self.assertEqual(tracking.cal, cal)
        self.assertEqual(tracking.selected, True)
        args = {"cal": cal.id, "add": 0}
        json_result = self.client.post('/f/tracking/select', args)
        self.assertEqual(len(TrackingCal.objects.all()), 1)
        tracking = TrackingCal.objects.all()[0]
        self.assertEqual(tracking.user, User.objects.get(username="Dave"))
        self.assertEqual(tracking.cal, cal)
        self.assertEqual(tracking.selected, False)

