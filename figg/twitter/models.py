from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from mainPage.models import Venue
from twitter import user_details_calculation
from datetime import datetime
from social_auth.models import UserSocialAuth
import logging
from twitter import MINI, NORMAL, BIGGER

# Get an instance of a logger
logger = logging.getLogger(__name__)


class TwitterLoad(models.Model):
    updated = models.DateTimeField(null=True)
    amount = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()
        super(TwitterLoad, self).save(*args, **kwargs)

    def __str__(self):
       return "%s %s" % (self.updated, self.amount)

class LoadTimes(models.Model):
    user = models.ForeignKey(User, related_name="user_obj")
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()
        super(LoadTimes, self).save(*args, **kwargs)

    def __str__(self):
       return "%s %s" % (self.updated, self.user)

class FollowerLoad(models.Model):
    followee = models.ForeignKey(User, related_name="followee")
    followers = models.ManyToManyField(User, related_name="followers")

    def __str__(self):
       return "%s %s" % (self.followee, self.followers)

class Tweets(models.Model):
    text = models.CharField(max_length=250)
    user = models.CharField(max_length=30) 
    tweet_time = models.DateTimeField()
    tweet_id = models.BigIntegerField()
    load = models.ForeignKey(TwitterLoad, null=True, blank = True)
    processable = models.NullBooleanField(null=True, blank = True)
   
    def __str__(self):
       return "%s %s %s %s %s %s" % (self.text, self.user, self.tweet_time, self.tweet_id, self.load, self.processable)

class UserDetails(models.Model):
   # set this to a default img
   DEFAULT = "default.png" 
   LARGE_DEFAULT = "default_large.png" 
   NORMAL_DEFAULT = "default_normal.png" 
   DEFAULT_SIZES = {MINI: DEFAULT, NORMAL: NORMAL_DEFAULT, BIGGER: LARGE_DEFAULT}

   user = models.OneToOneField(User, related_name = "user_details", unique = True)
   description = models.CharField(max_length=250, null=True, blank = True)
   user_img_mini = models.CharField(max_length=250, default = DEFAULT)
   user_img_normal = models.CharField(max_length=250, default = NORMAL_DEFAULT)
   user_img_bigger = models.CharField(max_length=250, default = LARGE_DEFAULT)
   url = models.URLField()

   def __str__(self):
       return "%s %s %s %s" % (self.user, self.user_img_mini, self.user_img_normal, self.user_img_bigger)

class EarlySignUp(models.Model):
    twitter_name = models.CharField(max_length=30)
    created = models.DateTimeField()
    updated = models.DateTimeField(null = True)

class PotentialEvent(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250, null = True, blank = True)
    img = models.CharField(max_length=250, null=True, blank = True)
    date = models.DateField()
    time = models.TimeField(null = True, blank = True)
    venue = models.ForeignKey(Venue, null = True, blank = True)
    publish = models.BooleanField(default = False)
    user = models.ForeignKey(User)

    def __unicode__(self):
       return "%s %s %s %s %s %s" % (self.title, self.date, self.time, self.venue, self.user.username, self.publish)

def create_user_details(sender, instance, created, **kwargs):
    if created:
        existing = UserDetails.objects.filter(user = sender)
        info = user_details_calculation.user_details(instance)

        if info:
            if existing:
                user_detail = existing[0]
            else:
                user_detail = UserDetails()

            for key, value in info.items():
                setattr(user_detail, key, value) 

            user_detail.save()

class EmailPending(models.Model):
    pending = models.ForeignKey(User)
    email_hash = models.IntegerField()
    amount = models.IntegerField(default = 0)
    updated = models.DateTimeField()

    def __str__(self):
        return "%s: %s %s" % (self.__class__, self.email_hash, self.updated)

    def save(self, *args, **kwargs):
        self.updated = datetime.utcnow()
        super(EmailPending, self).save(*args, **kwargs)

post_save.connect(create_user_details, sender=UserSocialAuth)



