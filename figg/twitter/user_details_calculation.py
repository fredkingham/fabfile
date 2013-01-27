from django.conf import settings
from django.contrib.auth.models import User 
from social_auth.models import UserSocialAuth
from django.utils import simplejson
import urllib, os, sys
import urllib2
import tweepy
from twitter import MINI, BIGGER, NORMAL, SIZES
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

SEARCH_URL = "http://search.twitter.com/search.json?q=%s&since_id=%s&page=%s"
IMG_API_URL = "https://api.twitter.com/1/users/profile_image?screen_name=%s&size=%s" 
RELATIVE_DIR = "../umedia"
PROFILE_DIR = settings.MEDIA_ROOT
OAUTH_TOKEN = "oauth_token"
OAUTH_SECRET = "oauth_token_secret"


# gets the json return of a url
def get_json(url):
    opener = urllib2.build_opener()
    f = opener.open(url)
    return simplejson.load(f)

def get_from_api(user, api, with_figg = False):
    try:

        if with_figg:
            me = api.get_user(user.username)
        else:
            me = api.me()

        img_url = me.profile_image_url

        change_token = "|< not a url >|"

        #replace last instance with something a template key
        count = img_url.count(NORMAL)

        replaced = img_url.replace(NORMAL, change_token)

        if count > 1:
            replaced = replaced.replace(change_token, NORMAL, count-1)

        result = {"url": img_url, "description": me.description}

        for size in SIZES:
            img_url = replaced.replace(change_token, size)
            username = user.username
            handler = urllib2.urlopen(img_url)
            redirect = handler.geturl()
            file_name = os.path.basename(redirect)
            user_dir = os.path.join(PROFILE_DIR, username)
            size_dir = os.path.join(user_dir, size)
            make_if_not_exists(user_dir)
            make_if_not_exists(size_dir)
            complete_file_name = os.path.join(size_dir, file_name)
            urllib.urlretrieve(img_url, complete_file_name)
            relative_name = os.path.join(os.path.join(username, size), file_name)
            result[size] = relative_name

        return result

    except:
        print 'the error is:', sys.exc_info()
        return {}


def make_if_not_exists(dir_name):
    if not os.path.exists(dir_name):
       os.mkdir(dir_name) 

def user_details(user_social_auth, api = False, safe = True):
    user = user_social_auth.user
    username = user

    if not api and not user_social_auth.extra_data:
        return
    elif not api and user_social_auth.extra_data:
        api = get_api(user_social_auth)

    result = get_from_api(user, api)
    if(not len(result)):
        logger.error("unable to get details for %s trying with F_i_g_g user")
        figg_api = get_api(UserSocialAuth.objects.get(user__username = "F_i_g_g"))
        result = get_from_api(user, figg_api)


    
    args= {}
    args["user"] = user
    args["url"] = result.get("url", "")
    args["description"] = result.get("description", "")
    mini = result.get(MINI)

    if mini:
        args["user_img_mini"] = mini

    normal = result.get(NORMAL)

    if normal:
        args["user_img_normal"] = normal

    bigger = result.get(BIGGER)

    if bigger:
        args["user_img_bigger"] = bigger

    return args

def get_user_details(user_social_auth):
    extra_details = user_social_auth.extra_data["access_token"].split("&")
    result = {}

    for extra_detail in extra_details:
        if OAUTH_SECRET in extra_detail:
            result[OAUTH_SECRET] = extra_detail.replace("%s=" % OAUTH_SECRET, "")
        elif OAUTH_TOKEN in extra_detail:
            result[OAUTH_TOKEN] = extra_detail.replace("%s=" % OAUTH_TOKEN, "")

    return result

def get_user_api(user):
    return get_api(UserSocialAuth.objects.get(user = user))

def get_api(user_social_auth):
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_TOKEN, settings.TWITTER_CONSUMER_SECRET)
    user_auths = get_user_details(user_social_auth)
    auth.set_access_token(user_auths[OAUTH_TOKEN], user_auths[OAUTH_SECRET])
    return tweepy.API(auth)





    
