from twitter.models import get_api
from social_auth.models import UserSocialAuth

'''loads from the PCC twitter feed'''
username = "figg_cinema"
user_social_auth = UserSocialAuth.objects.get(user__username = username)
api = get_api(user_social_auth)
pcc = api.get_user("ThePCCLondon")
twitter_id = pcc.id

