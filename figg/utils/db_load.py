from datetime import date, time, datetime, timedelta
from mainPage.models import *
from mainPage import constants
from mainPage.venue_calculation import store_long_lat
from django.contrib.auth.models import User


def load_db():
    chosen_few = [
            { "user": "fredkingham" },
            { "user": "rozbulleid" },
            { "user": "DiarmuidMoloney" },
            { "user": "TomKing2000" },
            { "user": "papersatellite" },
            { "user": "F_i_g_g" },
            { "user": "figg_cinema" },
            { "user": "grahamlyons" },
            { "user": "MegMcDonald1" },
            { "user": "__phin" }
            ]

    for chosen in chosen_few:
        ChosenFew.objects.get_or_create(**chosen)

