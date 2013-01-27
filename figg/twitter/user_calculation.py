from django.contrib.auth.models import User
from mainPage.models import ChosenFew
from twitter.models import UserDetails, FollowerLoad
from twitter import MINI, SIZES
from twitter.models import EarlySignUp
from datetime import datetime
from django.db.models import Q
from common import email_me


class UserDisplay(object):
    def __init__(self, row):
        self.img = row["user_details__user_img_mini"]
        self.user = row["username"]

    def as_json(self):
        return self.__dict__


def decode_tweet_id(tweet_id):
    if tweet_id[0] != "t":
        raise "incorrect tweet id passed in"
    else:
        return tweet_id[1:]


def encode_tweet_id(tweet_id):
    return "t%s" % tweet_id


def get_followers(user):
    return FollowerLoad.objects.get(followee=user).followers.all()


def get_all_users():
    chosen = ChosenFew.objects.all().values_list("user", flat=True)
    details = UserDetails.objects.filter(user__is_superuser=False, user__username__in=chosen)
    displays = []
    for detail in details:
        displays.append({"name": detail.user.username, "img": detail.user_img_mini, "id": encode_tweet_id(detail.id)})

    return displays


def search_users(user_search_term):
    users = User.objects.filter(Q(username__icontains=user_search_term) |
            Q(first_name__icontains=user_search_term) |
            Q(last_name__icontains=user_search_term))

    users = users.filter(is_superuser=False)
    users = users.order_by("last_login")
    users = users.values("username", "user_details__user_img_mini")
    users = users[:15]
    user_displays = [UserDisplay(i) for i in users]
    more = len(users) >= 15
    return {"users": user_displays, "more": more}

def get_invitees(user, tweet_user_id=None):

    query = FollowerLoad.objects.filter(followee__username=user)

    users = query.values_list("followers", flat=True)
    details = UserDetails.objects.filter(user__in=users)

    if tweet_user_id:
        display_id = decode_tweet_id(tweet_user_id)
        details = details.filter(id__gt=display_id)

    displays = []
    for detail in details:
        displays.append({"name": detail.user.username, "img": detail.user_img_mini, "id": encode_tweet_id(detail.id)})


    return displays

def get_user_details(users, size=MINI):
    size_field = SIZES[size]
    user_details = UserDetails.objects.filter(user__in=users).values[user, size_field]
    return user_details

def get_usernames(tweet_ids):
    display_ids = [decode_tweet_id(tweet_id) for tweet_id in tweet_ids] 
    return UserDetails.objects.filter(id__in=display_ids).values_list("user__username", flat=True)


def get_imgs(usernames, size=MINI):
    size_field = SIZES[size]
    args = {size_field: None}
    user_imgs = UserDetails.objects.filter(user__username__in=usernames).exclude(**args).values("user__username", size_field)
    user_info = dict((img["user__username"], img[size_field])for img in user_imgs)

    for username in usernames:
        if username not in user_info:
            user_info[username] = UserDetails.DEFAULT_SIZES[size]

    return user_info

def sign_up(twitter):
    result = {}
    result["val"] = "Something wrong happened... please refresh the page"
    result["issue"] = 1

    if not twitter:
        result["val"] = "please enter a name"
        return result


    if User.objects.filter(username=twitter):
        result["val"] =  "Sorry that user/email is taken"
        return result

    email_me.send("just signed up %s" % twitter, "just so you know")
    if not EarlySignUp.objects.filter(twitter_name = twitter):
        EarlySignUp.objects.create(twitter_name=twitter, created=datetime.now())

    result["val"] = "Great, we'll try and get you on board asap"

    result["issue"] = 0

    return result
