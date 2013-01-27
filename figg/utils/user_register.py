import sys
sys.path.append('$PROJECT_HOME')
from django.conf import settings
from django.core.management import setup_environ
from datetime import date, time, datetime, timedelta
setup_environ(settings)
from mainPage.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

form = UserCreationForm()

data = []
data.append({ "username" : "Askew", "password" : "Askew", "email" : "known@known.com"})
data.append({ "username" : "MentionTheWar", "password" : "MentionTheWar", "email" : "known@known.com"})

for user_struct in data:
    user = User.objects.create_user(user_struct["username"], user_struct["email"], user_struct["password"])
    user.save()


