from django.contrib.auth.models import User
from datetime import date
from common.user_tag import UserTag
from mainPage import event_calculation

def quick_load(cal = None, tag = None, end_key = None, end_date = None, start_key = None, start_date = None, username = None):

    if not start_date and not start_key and not end_date and not end_key:
        start_date = date.today()

    if not username:
        username = "fredkingham"

    cal_tag = UserTag(tag = tag, user = cal)
    start_key = None
    end_key = None
    user = User.objects.get(username = username)
    args = {'end_key': end_key, 'end_date': end_date, 'start_date': start_date, 'start_key': start_key, 'user_tags': [cal_tag], 'user': user}
    event_holder = event_calculation.calculate_events(**args)
    return event_holder

