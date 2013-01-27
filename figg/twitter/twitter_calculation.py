from django.utils import simplejson
from django.db.models import Q
from twitter.models import TwitterLoad, Tweets, FollowerLoad, LoadTimes, UserDetails
from twitter import user_details_calculation
from social_auth.models import UserSocialAuth
from common import timer
from django.db.models import Max
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from social_auth.models import UserSocialAuth
from twitter import data_extract, get_twitter_info
from mainPage import event_creator
import sys, traceback, re, tweepy, logging, urllib, urllib2
from django.core.mail import send_mail 

SEARCH_URL = "http://search.twitter.com/search.json?q=%s&since_id=%s&page=%s"
search_term = "(fi.gg)"
max_load = "60"

# Get an instance of a logger
logger = logging.getLogger(__name__)
FOLLOWERS_URL = "http://api.twitter.com/1/followers/ids.json?screen_name=%s"
FRIENDS_URL = "http://api.twitter.com/1/friends/ids.json?screen_name=%s"
FRIENDS_FOLLOWERS_COUNT_LIMIT = 140
OAUTH_TOKEN = "oauth_token"
OAUTH_SECRET = "oauth_token_secret"

def recent_loads(user):
    now = datetime.now()
    previous_hour = now - timedelta(hours=1)
    last_load = LoadTimes.objects.filter(updated__gte = previous_hour)

    if len(last_load) > 100:
        return False;

    for previous_load in last_load:
        if previous_load.user == user:
            return False

    return True

def safe_decorator(function):
    def email_issues(*args, **kwargs):   
        try:
            return function(*args, **kwargs)
        except:
            level = 6
            error_type, error_value, trbk = sys.exc_info()
            tb_list = traceback.format_tb(trbk, level)    
            s = "Error: %s \nDescription: %s \nTraceback:" % (error_type.__name__, error_value)
            for i in tb_list:
                s += "\n" + i
            error_msg = 'something using the safe decorator has broken, with %s from %s using %s and %s' % (function, s, args, kwargs)
            error_title = "error in twitter_calculation"
            send_mail(error_title, error_msg, 'fred@fi.gg', ['fredkingham@gmail.com'])
            raise

    return email_issues

def get_or_create_follower_load(user):
    return FollowerLoad.objects.get_or_create(followee = user)

def store_followers(api, user):
    friends = list() 
    
    for friend in tweepy.Cursor(api.friends).items():
        friends.append(friend.screen_name)
    
    friends_objs = User.objects.filter(username__in = friends)
    new_followers = set(User.objects.filter(username__in = friends))
    follower_obj_tuple = get_or_create_follower_load(user)
    follower_obj = follower_obj_tuple[0]

    if follower_obj_tuple[1]:
        followers = set(follower_obj.followers.all())
        to_remove = followers.difference(new_followers)

        if to_remove:
            follower_obj.followers.remove(*to_remove)

    new_followers = User.objects.filter(username__in = friends).exclude(followers__followee__username__in = friends)
    follower_obj.followers.add(*new_followers)

def save_details(user_social_auth, api = False, safe = True):
    details = user_details_calculation.user_details(**locals())
    existing = UserDetails.objects.filter(user = user_social_auth.user)
    info = user_details_calculation.user_details(user_social_auth)

    if existing:
        user_detail = existing[0]
    else:
        user_detail = UserDetails()

    for key, value in info.items():
        setattr(user_detail, key, value) 

    user_detail.save()

def store_friends_and_followers(username, force_load = False):
    user = User.objects.get(username = username)

    if recent_loads(user) or force_load:
        new_load = LoadTimes(user = user)
        new_load.save()
        user_social_auth = UserSocialAuth.objects.get(user = user)
        api = user_details_calculation.get_api(user_social_auth)
        store_followers(api, user)
        save_details(user_social_auth, api)

def get_user_details(user):
    extra_details = UserSocialAuth.objects.get(user = user).extra_data["access_token"].split("&")
    result = {}

    for extra_detail in extra_details:
        if OAUTH_SECRET in extra_detail:
            result[OAUTH_SECRET] = extra_detail.replace("%s=" % OAUTH_SECRET, "")
        elif OAUTH_TOKEN in extra_detail:
            result[OAUTH_TOKEN] = extra_detail.replace("%s=" % OAUTH_TOKEN, "")

    return result

def get_tweet_page(since_id=0, page=1):
    url_params=("fi.gg", since_id, page)
    json_query = SEARCH_URL % url_params
    json  = simplejson.load(urllib.urlopen(json_query))
    return json

def get_tweets(since_id = 0):
    results = []
    a = tweepy.Cursor(tweepy.api.search, search_term, since_id = since_id)
    total_time = 0
    twitter_load = TwitterLoad()
    twitter_load.save()

    for i in a.items(max_load):
        if search_term in i.text:
            results.append(i)

    logger.info("beginning twitter load")
    for result in results:
        args = {}
        args["text"] = result.text
        args["user"] = result.from_user
        args["tweet_time"] = result.created_at
        args["load"] = twitter_load
        args["tweet_id"] = result.id

        Tweets.objects.create(**args)

    logger.info("ending twitter load")
    twitter_load.amount = len(results)
    twitter_load.save()

def get_unprocessed_tweet_ids():
    return Tweets.objects.filter(processable=None).values_list('load_id', flat=True).distinct()

@timer.time_it_decorator
@safe_decorator
def extract_tweets():
    since_id = Tweets.objects.all().aggregate(Max("tweet_id"))["tweet_id__max"]
    new_twitter_load = TwitterLoad()
    results = get_tweets(since_id)
    process_tweets()

def process_tweets():
    valid_tweets = clean_tweets()
    save_tweets(valid_tweets)

def clean_tweets(): 
    all_tweets = Tweets.objects.filter(processable = None)
    all_tweets = all_tweets.exclude(Q(text__icontains = "(fi.gg") | Q(text__icontains = "(figg)"))
    all_tweets.update(processable = False)

    all_tweets = Tweets.objects.filter(processable = None)
    users = all_tweets.values_list('user', flat = True)
    figg_users = User.objects.filter(username__in = users).values_list('username', flat = True)
    all_tweets = all_tweets.exclude(user__in = figg_users)
    all_tweets.update(processable = False)

    valid_tweets = Tweets.objects.filter(processable = None)
    return valid_tweets

def save_tweets(valid_tweets):
    for tweet in valid_tweets:
        date_and_time = data_extract.extract_text(tweet.text)

        if not User.objects.filter(username = tweet.user).exists() or not date_and_time:
            tweet.processable = False
        else:
            user = User.objects.get(username = tweet.user)
            invitees = data_extract.get_invited(tweet.text)
            title = tweet.text
            description = None

            if len(tweet.text) > 100:
                title = tweet.text[:100]
                description = tweet.text[100:]

            event_creator.submit_event(event_date = date_and_time[0], title = title, description = description, user = user, event_time = date_and_time[1], invited = invitees)
            tweet.processable = True

        tweet.save()

