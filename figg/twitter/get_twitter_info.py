from django.conf import settings
from django.contrib.auth.models import User 
from django.utils import simplejson
import urllib, os, sys
import urllib2
from twitter import MINI, BIGGER, NORMAL, SIZES

SEARCH_URL = "http://search.twitter.com/search.json?q=%s&since_id=%s&page=%s"
IMG_API_URL = "https://api.twitter.com/1/users/profile_image?screen_name=%s&size=%s" 
RELATIVE_DIR = "../umedia"
PROFILE_DIR = settings.MEDIA_ROOT


# gets the json return of a url
def get_json(url):
    opener = urllib2.build_opener()
    f = opener.open(url)
    return simplejson.load(f)

def get_user_details(user, api):
    try:
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

def get_user_objs(usernames):
    UserDetails.objects.all()

def save_details(user_social_auth, api = False, safe = True):
    user = user_social_auth.user
    username = user

    if not api and not user_social_auth.extra_data:
        return
    elif not api and user_social_auth.extra_data:
        api = get_api(user_social_auth)

    result = user_details_calculation.get_user_details(user, api)

    existing = UserDetails.objects.filter(user = user)
    
    if existing:
        if len(existing) > 1:
            raise "multple existing found"

        user_details = existing[0]
        
        if user_details.url == result["url"] and user_details.user_img_bigger and user_details.user_img_normal and safe:
            logger.info("url hasn't changed from %s, returning" % user_details.url)
    else:
        user_details = UserDetails(user = user)
        user_details.url = result.get("url", "")

    user_details.description = result.get("description", "")
    mini = result.get(user_details_calculation.MINI)

    if mini:
        user_details.user_img_mini = mini

    normal = result.get(user_details_calculation.NORMAL)

    if normal:
        user_details.user_img_normal = normal

    bigger = result.get(user_details_calculation.BIGGER)

    if bigger:
        user_details.user_img_bigger = bigger

    user_details.save()




    
