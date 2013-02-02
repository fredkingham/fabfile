from django.conf import settings
from hotqueue import HotQueue
queue = HotQueue(settings.QUEUE_NAME)
from django.contrib.auth.models import User
from mainPage.models import *
from mainPage import event_creator
from notifications.models import *
from twitter.models import *
from figg_calendar.models import *
from web_crawler.models import *
from datetime import date


def clean_queue():
    assert(settings.TEST)
    assert(settings.QUEUE_NAME == "test")
    while(queue.get()):
        pass


def create_tag():
    """ creates an event and saves the tag hello with it """
    create_event({"description": "#hello"})


def create_venue():
    """ creates a new venue without spawning a lat/long process """
    name = "my house"
    address = "my road"
    postcode = "NOT REAL"
    creator = User.objects.all()[0]
    public = True
    new_venue = Venue(name=name, address=address, postcode=postcode, public=public, creator=creator)
    new_venue.save()
    return new_venue


def get_event_args():
    """ careful if called from a library method this is evaluated at the
    beginning"""
    user = User.objects.get(username="fredkingham")

    event_args = {
            'description': None,
            'title': u'something today',
            'user': user,
            'event_date': date(2012, 6, 20),
            'public': True
            }
            #'invited': set([])}
    return event_args.copy()


def create_event(custom_args=None):
    args = get_event_args()

    if custom_args:
        for custom_item, custom_value in custom_args.items():
            args[custom_item] = custom_value

    event_creator.submit_event(**args)


def populate():
    assert(settings.TEST)
    User.objects.create_user('Dave', 'Dave@gmail.com', 'Davepassword')
    User.objects.create_user('Bob', 'Bob@gmail.com', 'Bobpassword')
    User.objects.create_user('Fred', 'Fred@gmail.com', 'Fredpassword')
    User.objects.create_user('fredkingham', 'fredkingham@gmail.com', 'Fredpassword')
    ChosenFew.objects.create(user="Dave")
    ChosenFew.objects.create(user="Bob")
    ChosenFew.objects.create(user="Gary")
    default_args = {}
    default_args["description"] = "blah"
    default_args["user_img_mini"] = "blah"
    default_args["user_img_normal"] = "blah"
    default_args["user_img_bigger"] = "blah"

    for name in ["Dave", "Bob", "Fred"]:
        user = User.objects.get(username=name)
        args = default_args.copy()
        args["user"] = user
        user_details = UserDetails(**args)
        user_details.save()

    follower = FollowerLoad(followee = User.objects.get(username = 'Dave'))
    follower.save()
    follower.followers.add(User.objects.get(username = "Fred"))
    display = {}
    display["user"] = User.objects.get(username = "fredkingham")
    display["description"] = "go figger"
    display["user_img_normal"] = u'fredkingham/normal/left_normal.png'
    UserDetails.objects.create(**display)
    TrackingCal.objects.all().delete()
    TrackingTag.objects.all().delete()
    TrackingVenue.objects.all().delete()
    TrackingSeries.objects.all().delete()

def clean_up():
    assert(settings.TEST)
    Event.objects.all().delete()
    AttendingStatus.objects.all().delete()
    InvitedStatus.objects.all().delete()
    Notification.objects.all().delete()
    Note.objects.all().delete()
    Tweets.objects.all().delete()
    PostedNotification.objects.all().delete()
    SelectedCal.objects.all().delete()
    TrackingCal.objects.all().delete()
    TrackingVenue.objects.all().delete()
    TrackingTag.objects.all().delete()
    TrackingSeries.objects.all().delete()
    ExtractStatus.objects.all().delete()
    clean_queue()

def total_clean_up():
    clean_up()
    EmailPending.objects.all().delete()
    User.objects.all().delete()
    UserDetails.objects.all().delete()
    TwitterLoad.objects.all().delete()
    Venue.objects.all().delete()
