from mainPage.models import AttendingStatus, InvitedStatus, Note, Tag, Event
from mainPage import tag_calculation, event_key
from collections import defaultdict  
from twitter import data_extract, user_calculation
from twitter.models import UserDetails, FollowerLoad
from django.conf import settings
from django.contrib.auth.models import User
from collections import defaultdict
from django.db.models import Q, Max
import sys, re
from common import misc_functions
import logging
from notifications import queue_writer
from datetime import datetime
import HTMLParser
_htmlparser = HTMLParser.HTMLParser()
unescape = _htmlparser.unescape

logger = logging.getLogger(__name__)

def get_description(description, user, invitees, event_date, event_time):
    if not description and (invitees or event_date):
        description = ""

        if invitees:
            description = "%s invited %s" % (user, ", ".join(invitees))
            if event_date:
                description = description + " and "

        if event_date:
            if event_time:
                date_time_string = "%s %s" % (event_date, event_time)
            else:
                date_time_string = str(event_date)

            if invitees:
                description = description + " and moved it to %s" % event_date
            else:
                description = description + "%s moved it to %s" % (user, event_date)

    return description

# the inviter has an attending status of invite, the invitee has an attending
# status of invited
# the invited status has a status of pending
# if the person has already said unable, let them re invite, change invite to ignore
# return the invited status of the users involved
def invite(user, invitees, event, public = True):
    ''' invites other users, if an invited status doesn't already exist between
    these 2 users, we create a new invited status and do the invite '''

    public = event.public
    invited_users = User.objects.filter(username__in = invitees)
    invite = AttendingStatus(status = AttendingStatus.INVITE, event = event, user = user, public = public)
    invite.save()

    for invited_user in invited_users:
        invitee_status = AttendingStatus(status = AttendingStatus.INVITED, event= event, user = invited_user, public = public)
        invitee_status.save()
        invited_status = InvitedStatus(from_attending_status = invite, to_attending_status = invitee_status)
        invited_status.save()
        args = [invited_status.id]
        queue_writer.invite(invited_user, invited_status)

    return 0

def invite_users(user, coded_event_id, invitee_usernames):
    event_time_id = misc_functions.decode_id(coded_event_id);
    invite(user, invitee_usernames, Event.objects.get(id = event_time_id))

# return a map of cal -> tags
def calculate_tags(cal):
    try:
        tags = User.objects.get(username = cal).tag_cals.values_list("name", flat=True)
        return tags
    except:
        print 'the error is:', sys.exc_info()
        return []

def get_note_count(event_time, user):
    return get_note_count_from_id(event_time.id, user)

def get_note_count_from_id(event_id, user):
    notes = Note.objects.filter(event = event_id)
    notes = notes.filter(Q(published__followers__followee = user) | Q(published = user) | Q(mentions = user))
    notes = notes.distinct().count()
    return notes

def get_note_count_for_event_ids(event_ids, user):
    notes = Note.objects.filter(event = event_id)
    notes = notes.filter(Q(published__followers__followee = user) | Q(published = user) | Q(mentions = user))
    notes = notes.distinct().count()
    return notes

def get_mentions(event_time_id, user):
    mentions = Note.objects.filter(event__id = event_id)
    mentions = mentions.filter(mentions = user)
    return mentions

def share_note(note_id, user):
    note = Note.objects.get(id = note_id)
    if user in note.published.all():
        note.published.remove(user)
    else:
        note.published.add(user)
        notify_share(note, user)

def get_attending_followers(note, user):
    follower_ids = FollowerLoad.objects.filter(followee = user)
    follower_ids = follower_ids.filter(followers__attending_status__event__note__id = note.id)
    follower_ids = follower_ids.values_list("followers", flat = True).distinct()
    return User.objects.filter(id__in = follower_ids)

def notify_new_comment(note, user):
    followers = get_attending_followers(note, user)
    for follower in followers:
        queue_writer.add_comment(follower, note)

def notify_new_change(detail, user):
    followers = get_attending_followers(detail.note, user)
    for follower in followers:
        queue_writer.change_time(follower, detail)

def notify_new_mentions(note, users):
    for user in users:
        queue_writer.add_mention(user, note)

def notify_share(note, user):
    followers = get_attending_followers(note, user)
    for follower in followers:
        queue_writer.add_share(follower, note)

def get_previous_event(note):
    query = Note.objects.filter(event__in = note.event.all())
    query = query.annotate(first = Min("updated"))
    query = query.values_list("event_times", flat = True)[0]
    return Event.objects.get(id = query)

def calculate_note(note, user):
    row = {}
    row["note_id"] = note.id
    row["creator"] = note.creator.username
    row["details"] = False 
    row["img"] = note.creator.user_details.user_img_normal
    row["description"] = unescape(note.description)
    shares = note.published.all()
    event= note.event

    if not event:
        raise "no event???"

    row["shares"] = calculate_shares(shares)
    row["shared"] = bool(shares.filter(id = user.id))
    row["title"] = event.title

    return row


def calculate_shares(query):
    shares = query.values("user_details__user_img_mini", "username")
    result = []
    for share in shares:
        result.append({"sharer": share["username"], "sharer_img": share["user_details__user_img_mini"]})

    if not result:
        return ""

    return result

def notes_from_args(event_id, user):
    event_time_id = misc_functions.decode_id(event_id)
    notes = get_notes(event_time_id, user)
    calculated_notes = []

    for note in notes:
        calculated_notes.append(calculate_note(note, user))

    return calculated_notes

def get_notes(event_id, user):
    notes = Note.objects.filter(event__id = event_id)
    notes = notes.exclude(description = None)
    notes = notes.filter(Q(published__followers__followee = user) | Q(published = user) | Q(mentions = user))
    notes = notes.distinct().order_by("updated")
    return notes

def get_date(event_date):
    if event_date:
        potential_date = data_extract.extract_text(event_date.upper())
        if potential_date:
            return potential_date[0]

    return None

def get_time(event_time):
    if event_time:
        return data_extract.get_time(event_time.upper())

    return None


def create_discuss(description, user, invitees, hashed_event_id):
    print "here with %s" % locals()
    #add any invitees mentioned in the description...
    mentioned = set(invitees) | set(data_extract.get_invited(description))
    event_id = misc_functions.decode_id(hashed_event_id)
    event_obj = Event.objects.get(id = event_id)
    note = create_note(description, user, mentioned, event_obj)
    mentioned_users = User.objects.filter(username__in = mentioned)
    notify_new_mentions(note, mentioned_users)
    notify_new_comment(note, user)

def create_note(description, user, mentions, event_obj):
    statuses = AttendingStatus.objects.filter(user = user, event= event_obj, public = False ).count()

    private = statuses > 0

    note = Note(description = description, creator = user, public = not private)
    note.event = event_obj
    note.save()
    note.published.add(user)

    if mentions:
        mentioned_users = User.objects.filter(username__in = mentions)

        for i in mentioned_users:
            note.mentions.add(i)

    #if invitees send this to the invitees add a notification
    tag_calculation.save_tags_for_notes(description, user, note, event_obj)

    return note


