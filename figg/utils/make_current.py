from datetime import date, time
from mainPage import event_calculation
from mainPage.models import *

Meg = "MegMcDonald1"
description = "Roddy Woomble at Borderline"
event_times = {"eventDate": "5May2012"}
event_times["time"] = "7pm"
event_calculation.create_events(Meg, [event_times], description, [])

description = "Thames River Pageant Party at the boss's house"
event_times = [{"eventDate": "3Jun2012", "time": ""}]
event_calculation.create_events(Meg, event_times, description, [])

graham = "grahamlyons"
diamuid = "DiarmuidMoloney"
description = "29May2012 London MongoDB User Group 2012 Meetup #4 @fredkingham"
event_times = [{"eventDate": "29May2012", "time": ""}]
event_calculation.create_events(diamuid, event_times, description, ["fredkingham"])

event = Event.objects.get(description = "29May2012 London MongoDB User Group 2012 Meetup #4 @fredkingham")
event_time = event.event_times.all()[0]
AttendingStatus(user = User.objects.get(username = graham), status = AttendingStatus.ADDED, event_time = event_time)

