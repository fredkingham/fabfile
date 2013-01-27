from django.db import models
from django.contrib.auth.models import User
from mainPage.models import Tag, Venue, EventSeries
from datetime import datetime

class AbstractTracking(models.Model):
    user = models.ForeignKey(User)
    last_viewed = models.DateTimeField()
    selected = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.last_viewed = datetime.utcnow()
        super(AbstractTracking, self).save(*args, **kwargs)

class TrackingCal(AbstractTracking):
    cal = models.ForeignKey(User, related_name="tracking_cal")


class TrackingTag(AbstractTracking):
    tag = models.ForeignKey(Tag)


class TrackingSeries(AbstractTracking):
    series = models.ForeignKey(EventSeries)


class TrackingVenue(AbstractTracking):
    venue = models.ForeignKey(Venue)
