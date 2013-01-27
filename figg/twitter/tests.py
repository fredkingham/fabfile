from django.utils import unittest
from datetime import date, timedelta, time
from twitter import data_extract, twitter_calculation, user_calculation
from twitter.models import *
from mainPage.models import *
from django.contrib.auth.models import User
from django.test.client import Client
from django.utils import simplejson
from common import test_functions
from django.test.client import Client
from django.utils import simplejson 


def populate_users():
    User.objects.create_user('Dave', 'Dave@gmail.com', 'Davepassword')
    User.objects.create_user('Bob', 'Bob@gmail.com', 'Bobpassword')
    User.objects.create_user('Gary', 'Gary@gmail.com', 'Garypassword')
    ChosenFew.objects.create(user = "Dave")
    ChosenFew.objects.create(user = "Bob")
    ChosenFew.objects.create(user = "Gary")
    User.objects.create_user('fredkingham', 'fredkingham@gmail.com', 'Fredpassword')
    display = {}
    display["user"] = User.objects.get(username = "fredkingham")
    display["description"] = "go figger"
    display["user_img_normal"] = u'fredkingham/normal/left_normal.png'
    UserDetails.objects.create(**display)

def clean_up():
    User.objects.all().delete()
    ChosenFew.objects.all().delete()
    UserDetails.objects.all().delete()
    Event.objects.all().delete()
    AttendingStatus.objects.all().delete()

class EmailValidation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    def test_decorator_when_not_chosen(self):
        c = Client()
        ChosenFew.objects.filter(user = "Dave").delete()
        c.login(username = 'Dave', password = 'Davepassword')
        response = c.get('/d/email_request/', follow=True)
        self.assertEqual(len(response.redirect_chain), 1)

        response = c.get('/d/email_request/Dave/100/', follow=True)
        self.assertEqual(len(response.redirect_chain), 1)

        ChosenFew.objects.create(user = "Dave")

    def test_decorator_when_no_email(self):
        c = Client()
        dave = User.objects.get(username = "Dave")
        dave.email = '' 
        dave.save()
        c.login(username = 'Dave', password = 'Davepassword')
        response = c.get('/d/email_request/', follow=True)
        self.assertEqual(len(response.redirect_chain), 0)
        response = c.get('/d/email_request/Dave/100/', follow=True)
        self.assertEqual(len(response.redirect_chain), 0)
        dave.email = 'Dave@gmail.com'
        dave.save()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

class EmailRequest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    def test_redirect_user_logged_in(self):
        dave = User.objects.get(username = "Dave")
        c = Client()
        c.login(username = 'Dave', password = 'Davepassword')
        response = c.get('/d/email_request/', follow=True)
        template_names = [x.name for x in response.template]
        self.assertIn("index.html", template_names)

    def test_email_form_no_error_no_args(self):
        dave = User.objects.get(username = "Dave")
        dave.email = '' 
        dave.save()
        c = Client()
        c.login(username = 'Dave', password = 'Davepassword')
        response = c.get('/d/email_request/', follow=True)
        template_names = [x.name for x in response.template]
        self.assertIn("email_request.html", template_names)
        self.assertIn("username", response.context)
        self.assertNotIn("error", response.context)
        dave.email = 'Dave@gmail.com'
        dave.save()

    def test_email_form_bad_email(self):
        dave = User.objects.get(username = "Dave")
        dave.email = 'asdfasdfsad' 
        dave.save()
        c = Client()
        c.login(username = 'Dave', password = 'Davepassword')
        response = c.get('/d/email_request/', follow=True)
        template_names = [x.name for x in response.template]
        self.assertIn("email_request.html", template_names)
        self.assertIn("email", response.context)
        self.assertIn("error", response.context)
        self.assertIn("flawed", response.context)
        dave.email = 'Dave@gmail.com'
        dave.save()

    def test_post_form_no_issues(self):
        self.assertEqual(len(EmailPending.objects.all()), 0)
        dave = User.objects.get(username = "Dave")
        email = dave.email
        dave.email = ""
        dave.save()
        c = Client()
        c.login(username = 'Dave', password = 'Davepassword')
        response = c.post('/d/email_request/', data={"email": email}, follow=True)
        self.assertEqual(len(EmailPending.objects.all()), 1)
        dbo = EmailPending.objects.all()[0]
        self.assertEqual(dbo.pending, dave)
        self.assertEqual(dbo.amount, 1)
        template_names = [x.name for x in response.template]
        self.assertIn("email_sent.html", template_names)
        self.assertNotIn("error", response.context)

        response = c.post('/d/email_request/', data={"email": email}, follow=True)
        self.assertEqual(len(EmailPending.objects.all()), 1)
        dbo = EmailPending.objects.all()[0]
        self.assertEqual(dbo.pending, dave)
        template_names = [x.name for x in response.template]
        self.assertIn("email_sent.html", template_names)
        self.assertNotIn("error", response.context)
        self.assertEqual(dbo.amount, 2)

        email = "fake@gmail.com"
        response = c.post('/d/email_request/', data={"email": email}, follow=True)
        self.assertEqual(len(EmailPending.objects.all()), 1)
        dbo = EmailPending.objects.all()[0]
        self.assertEqual(dbo.pending, dave)
        template_names = [x.name for x in response.template]
        self.assertIn("email_sent.html", template_names)
        self.assertNotIn("error", response.context)
        self.assertEqual(dbo.amount, 1)

        email = "fake"
        response = c.post('/d/email_request/', data={"email": email}, follow=True)
        template_names = [x.name for x in response.template]
        self.assertIn("email_request.html", template_names)
        self.assertIn("error", response.context)
        self.assertEqual(len(EmailPending.objects.all()), 0)

        email = "fake@gmail.com"
        response = c.post('/d/email_request/', data={"email": email}, follow=True)
        self.assertEqual(len(EmailPending.objects.all()), 1)
        dbo = EmailPending.objects.all()[0]
        self.assertEqual(dbo.pending, dave)
        template_names = [x.name for x in response.template]
        self.assertIn("email_sent.html", template_names)
        self.assertNotIn("error", response.context)
        self.assertEqual(dbo.amount, 1)

        email_hash = dbo.email_hash
        username = dbo.pending.username
        url = '/d/email_request/%s/%s/' % (username, email_hash - 1)
        response = c.get(url)
        template_names = [x.name for x in response.template]
        self.assertIn("email_sent.html", template_names)
        self.assertNotIn("error", response.context)

        email_hash = dbo.email_hash
        username = dbo.pending.username
        url = '/d/email_request/%s/%s/' % (username, email_hash)
        response = c.get(url)
        template_names = [x.name for x in response.template]
        self.assertIn("email_confirmed.html", template_names)
        self.assertEqual(len(EmailPending.objects.all()), 0)
        self.assertNotIn("error", response.context)

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

class DataExtractTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

    def test_event_info_process(self):
        c = Client()
        logged_in  = c.login(username = 'Dave', password = 'Davepassword')
        result = c.post('/!event_info_process', {'data': ' '})
        from_json = simplejson.loads(result.content)
        self.assertEqual(from_json, {"date": None, "time": None})

    def testDateTimeExtraction(self):
        current_year = date.today().year
        current_month = date.today().month
        today = date.today()


        Sat21122012 = date(2012, 01, 21)
        Sun22122012 = date(2012, 01, 22)
        NextTues = date(2012, 01, 24)

        test_cases = {
        "hey let's meet tomorrow?": (Sat21122012 + timedelta(1), None),
        "what are you up to next week?": None,
        "are you free on the 8th of Jun?": (date(Sat21122012.year, 6, 8), None),
        "are you free today at 10?": (Sat21122012, time(10)) ,
        "how about we meet on the 1st at 10?": (date(Sat21122012.year, Sat21122012.month + 1, 1), time(10)),
        "how does January the 1st work for you?": (date(Sat21122012.year + 1, 1, 1), None),
        "maybe at 9pm?": (Sat21122012, time(21)),
        "how about we meet up next Tuesday at 10? (fi.gg)": (NextTues, time(10)),
        "I could do 9Sep12?": (date(2012, 9, 9), None),
        "I could do 9 Sep 12?": (date(2012, 9, 9), None),
        "I could do 9 September 12?": (date(2012, 9, 9), None),
        "I could do 9 September 2012?": (date(2012, 9, 9), None),
        "I could do 23 Aug 2012" : (date(2012, 8, 23), None),
        "I don't contain a date": None,
        "see you at 10:00": (Sat21122012, time(10)),
        "Wed Aug 15 2012 00:00:00 GMT+0100 (BST)": (date(2012, 8, 15), time(0))
        }

        
        for case, expected in test_cases.items():

            found = data_extract.extract_text(case, Sat21122012)

            self.assertEqual(found, expected, "failed for %s, should have been %s, returned %s" % (case, expected, found))


        # test sunday next Tuesday
        case = "how about we meet up next Tuesday at 10? (fi.gg)"
        found = data_extract.extract_text(case, Sun22122012)
        expected = (NextTues + timedelta(weeks=1), time(10))
        self.assertEqual(found, expected, "failed for %s, should have been %s, returned %s" % (case, expected, found))

class UserDisplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_functions.populate()

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()
    
    def test_search_users(self):
        user_display_holder = user_calculation.search_users("Dav")
        self.assertIn("users", user_display_holder)
        self.assertIn("more", user_display_holder)
        self.assertEqual(len(user_display_holder["users"]), 1)
        user_display = user_display_holder["users"][0]
        self.assertEqual(user_display.user, "Dave")
        self.assertEqual(user_display.img, "blah")

    def test_search_user_view(self):
        c = Client()
        json_response = c.get('/!search_users/', {'search_term': 'Da', 'forDate': 20120910})
        response = simplejson.loads(json_response.content)
        self.assertFalse(response["more"])
        self.assertIn("users", response)
        self.assertEqual(len(response["users"]), 1)

class TwitterLoadTest(unittest.TestCase):

    def createTweetArgs(self):
        args = {}
        args["text"] = "There you go, here's an event and everything for tomorrow (fi.gg)"
        args["user"] = User.objects.get(username = "fredkingham")
        args["tweet_time"] = datetime.now()
        args["tweet_id"] = 1
        args["load"] = TwitterLoad.objects.all()[0]
        args["processable"] = None
        return args.copy()

    @classmethod
    def createTwitterLoad(self):
        args = {}
        args["amount"] = 1
        twitter_load = TwitterLoad(**args)
        twitter_load.save()

    @classmethod
    def setUpClass(self):
        test_functions.populate()
        self.createTwitterLoad()

    def tearDown(self):
        test_functions.clean_up()

    def testTwitterLoad(self):
        args = self.createTweetArgs()
        Tweets.objects.create(**args)
        self.assertEqual(len(Event.objects.all()), 0)
        twitter_calculation.process_tweets()
        self.assertEqual(len(Event.objects.all()), 1)

    def test_clean_tweets_no_brackets(self):
        args = self.createTweetArgs()
        args["text"] = "Fi.gg alsdkjfasldkfjdslkjf"
        Tweets.objects.create(**args)
        twitter_calculation.clean_tweets()
        self.assertEqual(len(Tweets.objects.filter(processable = False)), 1)
        self.assertEqual(len(Tweets.objects.all()), 1)

    def test_clean_tweets_unknown_user(self):
        args = self.createTweetArgs()
        args["user"] = "asdlfkjasd"
        Tweets.objects.create(**args)
        twitter_calculation.clean_tweets()
        self.assertEqual(len(Tweets.objects.filter(processable = False)), 1)
        self.assertEqual(len(Tweets.objects.all()), 1)
        
    def test_a_single_valid_tweet(self):
        args = self.createTweetArgs()
        args["user"] = "asdlfkjasd"
        Tweets.objects.create(**args)
        args = self.createTweetArgs()
        args["text"] = "Fi.gg alsdkjfasldkfjdslkjf"
        Tweets.objects.create(**args)
        args = self.createTweetArgs()
        Tweets.objects.create(**args)
        twitter_calculation.clean_tweets()
        self.assertEqual(len(Tweets.objects.filter(processable = False)), 2)
        self.assertEqual(len(Tweets.objects.all()), 3)
        self.assertEqual(len(Tweets.objects.filter(processable = None)), 1)
        self.assertEqual(len(Tweets.objects.filter(processable = True)), 0)

    def test_save_a_tweet(self):
        args = self.createTweetArgs()
        Tweets.objects.create(**args)
        twitter_calculation.save_tweets(Tweets.objects.all())
        self.assertEqual(len(Tweets.objects.all()), 1)
        self.assertEqual(len(Tweets.objects.filter(processable = True)), 1)
        self.assertEqual(len(AttendingStatus.objects.all()), 2)

        user = User.objects.get(username = "fredkingham")
        creators = AttendingStatus.objects.filter(status = AttendingStatus.CREATOR )
        self.assertEqual(len(creators), 1)
        self.assertEqual(creators[0].user, user)

        addeds = AttendingStatus.objects.filter(status = AttendingStatus.ADDED)
        self.assertEqual(len(addeds), 1)
        self.assertEqual(addeds[0].user, user)
        self.assertEqual(len(Event.objects.all()), 1)
        tomorrow = date.today() + timedelta(1)
        event = Event.objects.all()[0]
        self.assertEqual(event.date, tomorrow)
        self.assertEqual(event.title, args["text"])

    def test_save_a_long_tweet(self):
        args = self.createTweetArgs()
        text = '''this is a very long tweet that invites @Bob, I'm hoping he
        really appreciates it, as we want to do something tomorrow and this is
        nice'''
        args["text"] = text
        Tweets.objects.create(**args)
        twitter_calculation.save_tweets(Tweets.objects.all())
        self.assertEqual(len(InvitedStatus.objects.all()), 1)
        invited_status = InvitedStatus.objects.all()[0]
        from_status = invited_status.from_attending_status
        tweet_user = User.objects.get(username = "fredkingham")
        self.assertEqual(from_status.user, tweet_user)
        to_status = invited_status.to_attending_status
        to_user = User.objects.get(username = "Bob")
        self.assertEqual(to_status.user, to_user)
        self.assertEqual(len(Event.objects.all()), 1)
        event = Event.objects.all()[0]
        self.assertEqual(event.title, text[:100])
        self.assertEqual(event.description, text[100:])

    @classmethod
    def tearDownClass(self):
        test_functions.total_clean_up()

