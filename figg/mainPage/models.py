from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import Adjust
from imagekit.processors.resize import ResizeToFit
from datetime import datetime
from django.contrib.auth.models import User
import os


class Venue(models.Model):
    name = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=250)
    public = models.BooleanField(default=True)
    website = models.CharField(max_length=250, null=True, blank=True)
    creator = models.CharField(max_length=50)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def venue_link(self):
        concat = "%s-%s" % (self.name, self.postcode)
        return concat.replace(" ", "_")

    def get_title(self):
        return "%s (%s)" % (self.name, self.postcode)

    def as_dict(self):
        return {"venue_link": self.venue_link(), "address": self.address, "title": self.get_title(), "lat": self.latitude, "lng": self.longitude}

    def __str__(self):
        return "Venue: %s, %s" % (self.name, self.postcode)


class VenueOwner(models.Model):
    venue = models.ForeignKey(Venue)
    user = models.CharField(max_length=50)


def upload_to(instance, filename):
    return os.path.join('events', str(instance.id), filename)


class EventImage(models.Model):
    img = models.ImageField(null=True, blank=True, upload_to=upload_to)
    large_img = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFit(height=100)], image_field='img', format='JPEG', options={'quality': 90})

    def __repr__(self):
        return "%s: %s" % (self.__class__, self.img)

    def __str__(self):
        return "%s: %s" % (self.__class__, self.img)


class EventSeries(models.Model):
    name = models.CharField(null=True, blank=True, max_length=100)


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250, null=True, blank=True)
    public = models.BooleanField(default=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    venue = models.ForeignKey(Venue, null=True, blank=True)
    deleted = models.BooleanField(default=False)
    key = models.BigIntegerField()
    img = models.ForeignKey(EventImage, null=True, blank=True)
    updated = models.DateTimeField()
    event_series = models.ForeignKey(EventSeries, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()

        super(Event, self).save(*args, **kwargs)

    class Meta:
        ordering = ['key']

    def __repr__(self):
        return "%s: %s %s %s %s %s" % (self.__class__, self.date, self.time, self.title, self.venue, self.deleted)

    def __str__(self):
        return "%s: %s %s %s %s %s" % (self.__class__, self.date, self.time, self.title, self.venue, self.deleted)


class AttendingStatus(models.Model):

# coming
    ADDED = "added"
    ADDED_SHORT = 0
    INVITED = "invited"
    INVITED_SHORT = 1
    ACCEPTED = "accepted"
    ACCEPTED_SHORT = 2
    INVITE = "invite"
    INVITE_SHORT = 3

# not coming
    UNABLE = "unable"
    UNABLE_SHORT = 4
    CANCELLED = "cancelled"
    CANCELLED_SHORT = 5
    CREATOR = "creator"
    CREATOR_SHORT = 6

    DISPLAY = [ADDED, ACCEPTED]
    USER_DISPLAY = [ADDED, ACCEPTED, INVITE, INVITED]
    COMING_STATUSES = [ADDED, INVITED, ACCEPTED, INVITE]

    ATTENDING_STATUS_CHOICES = {
            ADDED: ADDED_SHORT,
            INVITED: INVITED_SHORT,
            INVITE: INVITE_SHORT,
            ACCEPTED: ACCEPTED_SHORT,
            UNABLE: UNABLE_SHORT,
            CANCELLED: CANCELLED_SHORT,
            CREATOR: CREATOR_SHORT
    }

    status = models.CharField(max_length=20)
    event = models.ForeignKey(Event, related_name="attending_status")
    user = models.ForeignKey(User, related_name="attending_status")
    public = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()
        super(AttendingStatus, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: status: %s, event: %s, user: %s" % (self.__class__, self.status, self.event, self.user)


class Note(models.Model):
    description = models.CharField(max_length=250, null=True, blank=True)
    event = models.ForeignKey(Event, null=True, blank=True)
    creator = models.ForeignKey(User, related_name="note_creator")
    published = models.ManyToManyField(User, related_name="note_published")
    mentions = models.ManyToManyField(User, related_name="note_mentions")
    public = models.BooleanField(default=True)
    updated = models.DateTimeField()
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()
        super(Note, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return "%s %s %s %s" % (self.description, self.event, self.creator, self.updated)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    notes = models.ManyToManyField(Note, related_name="notes")
    events = models.ManyToManyField(Event, related_name="tags")
    """ cals is the amount of users who's voted for this """
    cals = models.ManyToManyField(User, related_name="tag_cals")
    removal_requested = models.ManyToManyField(User, related_name="tag_removal")

    def __repr__(self):
        return "Tag: %s %s %s %s" % (self.name, self.events, self.notes, self.cals)

    def __str__(self):
        return "Tag: %s %s %s %s" % (self.name, self.events, self.notes, self.cals)

    def natural_key(self):
        return (self.name)


class SelectedCal(models.Model):
    cal_type = models.CharField(max_length=30)
    cal = models.CharField(max_length=30, null=True, blank=True)
    user = models.CharField(max_length=30)
    tag = models.ForeignKey(Tag, null=True, blank=True)
    last_viewed = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.last_viewed = datetime.utcnow()
        super(SelectedCal, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s %s %s" % (self.cal_type, self.cal, self.tag, self.user, self.last_viewed)


class RevealedCal(models.Model):
    cal_type = models.CharField(max_length=30)
    cal = models.CharField(max_length=30, null=True, blank=True)
    user = models.CharField(max_length=30)
    last_viewed = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.last_viewed = datetime.utcnow()
        super(RevealedCal, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s %s" % (self.cal_type, self.cal, self.user, self.last_viewed)


class ViewedCalendar(models.Model):
    viewer = models.CharField(max_length=30)
    viewed = models.CharField(max_length=30)
    viewed_tag = models.ForeignKey(Tag, null=True, blank=True)
    selected = models.BooleanField()
    last_viewed = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.last_viewed = datetime.utcnow()
        super(ViewedCalendar, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s %s" % (self.viewer, self.viewed, self.selected, self.last_viewed)


class InvitedStatus(models.Model):
    from_attending_status = models.ForeignKey(AttendingStatus, related_name="to_invited_status")
    to_attending_status = models.ForeignKey(AttendingStatus, related_name="from_invited_status")

    def __str__(self):
        return "%s, %s" % (self.from_attending_status, self.to_attending_status)


class ChosenFew(models.Model):
    user = models.CharField(max_length=30)

    def __str__(self):
        return "%s" % self.user
