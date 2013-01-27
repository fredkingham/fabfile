from django.contrib.auth.models import User
from mainPage.models import ChosenFew
from twitter.models import EmailPending

SALT = "blah1"

def one_of_the_chosen_few(user):
    return ChosenFewDB.objects.filter(user = request.user.username).exists()

def email_valid(user):
    return True
    return user.email and not EmailPending.objects.filter(pending = user).exists()

def get_hash(user):
    return str(abs(hash(SALT + user.username)))[:4]




