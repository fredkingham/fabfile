from django.contrib.auth.models import User
from loader import Loader
from datetime import date, time, timedelta

''' loads whole bunch of events as of 20June2012 '''

figg_film = User.objects.get(username = "figg_film")
figg_theatre = User.objects.get(username = "figg_theatre")
figg_lates = User.objects.get(username = "figg_lates")
figg_sport = User.objects.get(username = "figg_sport")


bfi = {
    "name" : "BFI Southbank",
    "address" : "Belvedere Road",
    "postcode" : "SE1 8XT",
    "public" : False,
    "creator" : "figg_film"
}

tricycle = {
    "name" : "The Tricycle Theatre",
    "address" : "269 Kilburn High Road",
    "postcode" : "NW6 7JR",
    "public" : False,
    "creator" : "figg_theatre"
}

the_pheonix = {
    "name" : "The Phoenix Cinema",
    "address" : "52 High Road",
    "postcode" : "N2 9PJ",
    "public" : False,
    "creator" : "figg_film"
}

london_zoo = {
    "name" : "ZSL London Zoo",
    "address" : "Regent's Park",
    "postcode" : "NW1 4RY",
    "public" : False,
    "creator" : "figg_lates"
}

electric_ballroom = {
    "name" : "The Electric Ballroom",
    "address" : "184 Camden High Street",
    "postcode" : "NW1 8QP",
    "public" : True,
    "creator" : "figg_lates"
}

the_national_theatre = {
    "name": "The National Theatre",
    "address": "The South Bank",
    "postcode": "SE1 9PX",
    "public" : True,
    "creator" : "figg_theatre"
}



loader = Loader()
public = True
invitees = []
description = None

def load_venues():
    loader.load_venues([bfi, tricycle, the_pheonix, london_zoo, electric_ballroom])
    loader.load_venues([the_national_theatre])

def load_tricycle_events():

    def load_Mary_Shelley():
        title = "Mary Shelley"
        user = figg_theatre
        i = date.today()
        event_times = loader.dateTimesForRange(date.today(), date(2012, 7, 8), time(20), excluding = [6])
        event_times.extend(loader.dateTimesForRange(date.today(), date(2012, 7, 8), time(14), including = [2, 5]))
        loader.load_events(title, figg_theatre, event_times, tricycle)

    def load_lovers_rock_monologues():
        title = "Lovers Rock Monologues"
        user = figg_theatre
        from_date = date(2012, 7, 9)
        to_date = date(2012, 7, 15)
        event_times = loader.dateTimesForRange(from_date, to_date, time(20))
        event_times.append({"date": date(2012, 7, 14), "time": time(16)})
        loader.load_events(title, figg_theatre, event_times, tricycle)

    load_Mary_Shelley()
    load_lovers_rock_monologues()

def load_zoo_lates():
        title = "ZSL London Zoo Lates"
        event_times = loader.dateTimesForRange(date.today(), date(2012, 7, 28), None, including = [4])
        if len(event_times):
            loader.load_events(title, figg_lates, event_times, london_zoo)


def load_ulimate_power_ballads():
        title = "ULTIMATE POWER"
        user = figg_lates
        power_description = "ULTIMATE POWER BALLADS"
        event_time = {"time": time(23), "date": date(2012, 6, 29)}
        loader.load_events(title, figg_lates, [event_time], electric_ballroom, description = power_description)

def load_national_theatre():

    def load_crow():
        title = "Crow in Greenwich"
        user = figg_theatre
        theatre_description = '''
        Breathing new theatrical life into Ted Hughes' mythic Crow poems, 
        this performance promises to be one of London's hottest tickets this summer.
        '''
        event_times = loader.dateTimesForRange(date.today(), date(2012, 7, 7), time(20), excluding = [6])
        loader.load_events(title, figg_theatre, event_times, the_national_theatre, description = theatre_description)

    load_crow()


