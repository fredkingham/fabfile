from social_auth.models import UserSocialAuth
from twitter.models import *
from twitter import twitter_calculation
from django.contrib.auth.models import User

def load_all_details():
    for i in UserSocialAuth.objects.all():
        twitter_calculation.save_details(i, safe = False)

#loads twitter followers if the guy has none at the moment
def store_twitter_followers():
    for i in UserSocialAuth.objects.all():
        user = i.user
        print "loading for %s" % user.username
        twitter_calculation.store_friends_and_followers(user.username, force_load = True)
            
