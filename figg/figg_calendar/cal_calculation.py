from figg_calendar import YOUR_CAL, INVITES, TWITTER_CALS, POPULAR_CALS, POPULAR_TAGS, CAL_TYPES
from mainPage.models import ViewedCalendar, AttendingStatus, InvitedStatus, Tag, SelectedCal, RevealedCal, Note
from django.contrib.auth.models import User
from datetime import datetime
from common.OrderedDict import OrderedDict
from twitter.models import UserDetails, FollowerLoad
import twitter
from mainPage import note_calculation, tag_calculation
from mainPage.tag_calculation import TagCalculated
from django.utils import simplejson
from datetime import date
from common.user_tag import UserTag, UserTagWithSelected
import inspect
from common.figgDate import FiggDate
from common.cal_holder import CalHolderWithSelected

# returns a hierachy of if the calendar or one of its tags is selected
def calculate_cal(cal_type, cal, username, cal_holder):
    """ returns a calculated cal, of calendar and tags """

# if selected return a selected calculated cal
# if revealed return a revealed calculated cal with tags attatched
    last_selected=SelectedCal.objects.filter(cal_type=cal_type, cal=cal, tag=None, user=username)
    last_revealed=RevealedCal.objects.filter(cal_type=cal_type, cal=cal, user=username)
    cal_holder.append(UserTagWithSelected(cal_type=cal_type, selected=bool(last_selected), revealed=bool(last_revealed)))

def calculate_popular_tags(cal_type, username, for_date, cal_holder):
    cal_holder.append(UserTagWithSelected(cal_type=cal_type))
    tag_dbos=tag_calculation.get_popular_tags(for_date)

    for tag_dbo in tag_dbos:
        cal_holder.append(UserTagWithSelected(cal_type=cal_type, tag=tag_dbo.name))

# username is false if the user is not logged in
def calculate_popular_calendars(cal_type, username, cal_holder, added_calendars=[], for_date=False):
    #for the time being just return 8 users that are in the attending status table
    #due to rubbish orms we will just take the first 8 events and stick their uses in a set meaning we could only get a single user
    cal_holder.append(UserTagWithSelected(cal_type=cal_type))
    already_covered=[i.cal for i in added_calendars]
    already_covered.append(username)
    popular_calendars=AttendingStatus.objects.exclude(user__username__in=already_covered).values_list("user__username", flat=True).distinct()

    viewed_users=set(popular_calendars)

    if len(viewed_users) < 8:
        users=User.objects.exclude(username=username).exclude(is_superuser=True)
        
        for added_calendar in added_calendars:
            users=users.exclude(username=added_calendar.cal)

        for viewed_user in viewed_users:
            users=users.exclude(username__in=popular_calendars)
       
        amount=8 - len(viewed_users)
        usernames=set(map(lambda a: a.username, users[:amount]))
        viewed_users=viewed_users | usernames
    
    for viewed_user in viewed_users:
        cal_holder.append(UserTagWithSelected(cal_type=cal_type, user=viewed_user))

def populate_default_cals(username):
    for cal_type in CAL_TYPES:
        SelectedCal.objects.create(user=username, cal_type=cal_type).save()
        RevealedCal.objects.create(user=username, cal_type=cal_type).save()

    return

# get all cals for this user and display them make sure they then don't appear
# in viewed calendars/popular calendars
def calculate_twitter_cals(cal_type, username, cal_holder):
    cal_holder.append(UserTagWithSelected(cal_type=cal_type))
    user=User.objects.get(username=username, is_superuser=False)
    follower_load=FollowerLoad.objects.get_or_create(followee=user)[0]
    follower_usernames=follower_load.followers.all().values_list("username", flat=True)
    selected_cals=SelectedCal.objects.filter(user=username, cal_type=cal_type, cal__in=follower_usernames).values_list("cal", flat=True)
    revealed_cals=RevealedCal.objects.filter(user=username, cal_type=cal_type, cal__in=follower_usernames).values_list("cal", flat=True)

    result =[]

    for follower_username in follower_usernames:
        user_tag=UserTagWithSelected(cal_type=cal_type, user=follower_username, selected=follower_username in selected_cals, revealed=follower_username in revealed_cals)
        cal_holder.append(user_tag)

def populate_cal_type(user, cal_types):
    cal_holder=calculate_calendars(user.username, cal_types, True)
    return cal_holder.exclude_cal_type_only()

# calculates the 4 types of calendar if they exist
# 1. Sponsored calendars (this needs the user definition, this can come later)
# 3. Trending calendars  (this needs consideration, do we want added calendars in the last week, changed calendars?)
# 4. Popular calendars (everyone should have this)
def calculate_calendars(username=False, cal_types=CAL_TYPES, get_cals=False, for_date=False):

    cal_holder=CalHolderWithSelected(user_username=username)

    if username: 
        already_done=[]
        for cal_type in cal_types:
            if cal_type == YOUR_CAL: 
                cal_holder.append(UserTagWithSelected(cal_type=cal_type))
                cal_holder.append(UserTagWithSelected(cal_type=cal_type, user=username))
            elif cal_type == TWITTER_CALS:
                calculate_twitter_cals(cal_type, username, cal_holder)
            elif cal_type == POPULAR_TAGS:
                calculate_popular_tags(cal_type, username, for_date, cal_holder)
            elif cal_type == POPULAR_CALS:
                calculate_popular_calendars(cal_type, username, cal_holder, already_done, for_date)

        cal_holder.get_display_info(twitter.BIGGER)
        cal_holder.update_selected_and_revealed()
        return cal_holder

def get_person_details(user):
    details={}
    try: 
        user_details=UserDetails.objects.get(user=user)
        img=user_details.user_img_bigger
        description=user_details.description
    except:
        img=UserDetails.LARGE_DEFAULT
        description=""

    try:
        followers=FollowerLoad.objects.get(user=user).followers.all()
        follower_details=UserDetails.objects.filter(user__in=followers).values("user__username", "user_img_mini")
        friends=FollowerLoad.objects.get(followers=user)
        friend_details=UserDetails.objects.filter(user=friends.user).values("user__username", "user_img_mini") 
    except:
        follower_details=[]
        friend_details=[]
        print 'unable to find anything about this user in follower details'

    added=AttendingStatus.objects.filter(user=user, status=AttendingStatus.ADDED).count()
    notes=Note.objects.filter(published=user).count()
    tags=note_calculation.calculate_tags(user.username)


    return {"cal": user.username, "description": description, "followers": follower_details, "friends": friend_details, "added": added, "notes": notes, "tags": tags, "img": img}

def get_tag_details(tag_name):
    ''' returns a dictionary with the tag, as well as users who have posted with this tag '''

    try: 
        tag=Tag.objects.get(name=tag_name)
    except:
        raise Http404

    details={}
    name=tag.name
    cals=tag.cals.all().values_list("username", flat=True)
    user_details=UserDetails.objects.filter(user__username__in=cals).values("user__username", "user_img_normal") 

    return {"tag": name, "added_users": user_details}


def get_selected_cals(calculated_cal_types):
    ''' takes in an map of calculated cal types and returns the ones cals that are selected as (cal, id_if_required) '''
    calendars_selected=[]
    
    for cal_type, cal_type_holder in calculated_cal_types.iteritems():
        if cal_type_holder.selected:
            for cal in cal_type_holder.cals:
                if cal.cal:
                    calendars_selected.append(UserTag(cal_type=cal_type, user=cal.cal))
                elif cal.tag:
                    calendars_selected.append(UserTag(cal_type=cal_type, tag=cal.tag.tag))
                else:
                    raise "cal holder is selected but no valid caltypes found for %s" % cal_type
        elif cal_type_holder.revealed or cal_type_holder.selected:
            for cal in cal_type_holder.cals:
                if cal.selected:
                    if cal.cal:
                        calendars_selected.append(UserTag(cal_type=cal_type, user=cal.cal))
                    elif cal.tag:
                        calendars_selected.append(UserTag(cal_type=cal_type, tag=cal.tag.tag))
                    else:
                        raise "unable to find a cal or tag for cal %s" % cal
                elif cal.revealed:
                    for tag in cal.tags:
                        if tag.selected:
                            calendars_selected.append(UserTag(cal_type=cal_type, user=cal.cal, tag=tag.tag))

    return calendars_selected

def reveal_cal(user_tag, username):
    args={"user": username, "cal_type": user_tag.cal_type, "cal": user_tag.user}
    exists=RevealedCal.objects.filter()

    if exists:
        exists.delete()
    else:
        a=RevealedCal(**args)
        a.save()

def remove_selected_calendar(user_tag, username):
    if user_tag.tag:
        tag_obj=Tag.objects.get(name=user_tag.tag)
    else:
        tag_obj=None

    selected_cals=SelectedCal.objects.filter(cal=user_tag.user, user=username, tag=tag_obj, cal_type=user_tag.cal_type).delete()


def add_viewed_calendar(user_tag, username):

    if user_tag.tag:
        tag_obj=Tag.objects.get(name=user_tag.tag)
    else:
        tag_obj=None

    if user_tag.user and user_tag.tag:
        if user_tag.user:
            viewed_cal=ViewedCalendar(viewer=username, viewed=user_tag.user, selected=selected)
        elif user_tag.tag:
            viewed_cal=ViewedCalendar(viewer=username, selected=selected)

        viewed_cal.viewed_tag=tag_obj
        viewed_cal.save()

    selectedCal=SelectedCal(cal=user_tag.user, user=username, tag=tag_obj, cal_type=user_tag.cal_type)
    selectedCal.save()

def selected_cals_for_user(user):
    selected=SelectedCal.objects.filter(user=user.username).values("cal_type", "cal", "tag__name")
    return [UserTag(user=select["cal"], tag=select["tag__name"], cal_type=select["cal_type"]) for select in selected]

def get_trackee_count(user):
    """ returns the number of people tracking this user"""
    if not FollowerLoad.objects.filter(followee=user).exists():
        return 0
    else:
        return FollowerLoad.objects.get(followee=user).followers.count()

def get_tracking_count(user):
    """ returns the number of people this user is tracking"""
    return FollowerLoad.objects.filter(followers=user).count()

def get_selected_tag_count(tag_name):
    return SelectedCal.objects.filter(tag__name=tag_name).count()






