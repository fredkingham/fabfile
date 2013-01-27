from django.template.loader import get_template
# from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from common import complex_encoder
from common.validation import safe_get
from figg_calendar import cal_calculation
from twitter import user_calculation, NORMAL
from mainPage.forms import PreviewForm, EventEditorForm, EventCreatorForm, EventImgForm, EventQueryArgsValidation, VenueForm, DateLineForm
from twitter.models import UserDetails
from django.utils.html import escape
from twitter.decorators import authenticated
from mainPage.attending_status_holder import AttendingStatusHolder
import logging
from django.template import RequestContext
from mainPage import venue_calculation, event_calculation, note_calculation, preview_calculation, event_creator, event_validation
from datetime import datetime, date

# Get an instance of a logger
logger = logging.getLogger(__name__)
encoder = complex_encoder.Encoder()


def get_attending(request):
    if request.method == "GET":
        event_time_id = safe_get(request.GET, "id")

        if event_time_id is not None:
            if request.user.is_authenticated():
                return HttpResponse(encoder.encode(AttendingStatusHolder(event_time_id, request.user)), mimetype="application/json")
            else:
                return HttpResponse(encoder.encode(AttendingStatusHolder(event_time_id)), mimetype="application/json")

    return HttpResponse(encoder.encode(1), mimetype="application/json")


def img_preview(request):
    if request.user.is_authenticated():
        form = EventImgForm(request.POST, request.FILES)
        if form.is_valid():
            m = form.save()
            args = {"img_id": m.id, "img_url": m.large_img.url}
            return HttpResponse(encoder.encode(args), mimetype='application/json')
        else:
            logger.error("img preview form failed with %s" % form.errors)

    logger.error("img failing the user is authenticated = %s" %
                 request.user.is_authenticated())
    return HttpResponse(encoder.encode("error"), mimetype='application/json')


def profile(request):
    t = get_template('registration/profile.html')
    html = t.render(RequestContext(
        request, {'user_authenticated': request.user.username}))
    return HttpResponse(html)


def get_dateline(request):
    if request.user.is_authenticated():
        form = DateLineForm(request.GET, request.FILES)
        if form.is_valid():
            args = form.cleaned_data
            args["user"] = request.user
            return HttpResponse(encoder.encode(event_calculation.get_dateline(**args)), mimetype='application/json')
        else:
            logger.error("form is invalid with %s" % form.errors)

    return HttpResponse(encoder.encode({}), mimetype='application/json')


def invite(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            invitee_usernames = request.POST.getlist('names[]')
            coded_event_id = request.POST.get("event")
            note_calculation.invite_users(request.user, coded_event_id, invitee_usernames)

    return HttpResponse()


def external(request):
    return HttpResponseRedirect("/mainPage")


def venue(request, venue="name_postcode"):
    user_details = {'authenticated': request.user.is_authenticated(
    ), 'username': request.user.username}

    t = get_template('venue.html')

    venue_info = venue_calculation.calculate_venue_structure(venue)
    html = t.render(RequestContext(
        request, {"user_details": user_details, "venue_info": venue_info}))

    return HttpResponse(html)


def commit_venue(request):
    if request.user.is_authenticated():
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.creator = request.user.username
            venue.save()
            venue_calculation.spawn_lat_long_populate(form.cleaned_data["address"], form.cleaned_data["postcode"])

    return HttpResponseRedirect("/mainPage")


def create_venue(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/login/")

    user_details = {'authenticated': request.user.is_authenticated(
    ), 'username': request.user.username}
    t = get_template('create_venue.html')
    html = t.render(RequestContext(request, {"user_details": user_details}))
    return HttpResponse(html)


def submit_venue(request):

    if not request.user.is_authenticated():
        return HttpResponse(encoder.encode({"error": "Please refresh your browser"}), mimetype='application/json')

    name = safe_get(request.POST, "name")
    address = safe_get(request.POST, "address")
    postcode = safe_get(request.POST, "postcode")
    private = request.POST.get('private') == 'true'
    username = request.user.username

    if not name:
        return HttpResponse(encoder.encode({"error": "Please give us a name"}), mimetype='application/json')

    if not address:
        return HttpResponse(encoder.encode({"error": "Please give us a address"}), mimetype='application/json')

    if not postcode:
        return HttpResponse(encoder.encode({"error": "Please give us a postcode"}), mimetype='application/json')

    venue_calculation.submit_venue(
        name, address, postcode, not private, username)

    return HttpResponse(encoder.encode({"success": 1}), mimetype='application/json')


def preview_creator(request):
    if request.method == 'POST' and request.user.is_authenticated():

        user_details = {'authenticated': request.user.is_authenticated(
        ), 'username': request.user.username}
        user = request.user

        details = cal_calculation.get_person_details(user)

        form = PreviewForm(request.POST)

        if not form.is_valid():
            logger.error("preview creator erroring with %s" % form.errors)
            raise Http404

        invites = []

        invitee_details = UserDetails.objects.filter(user__username__in=form.cleaned_data['invited'].split(',')).values("user__username", "user_img_normal")
        # calculate amount and relevent dates....
        new_dates = preview_calculation.calculate_preview(form.cleaned_data['when'], form.cleaned_data['time'], form.cleaned_data['repeat_event'], form.cleaned_data['repeat_until'])
        img = user_calculation.get_imgs(
            [request.user.username], NORMAL)[request.user.username]
        t = get_template('preview.html')
        preview_details = {"new_dates": new_dates, "description": form.cleaned_data['what'], "title": form.cleaned_data['title'], "venue": form.cleaned_data['venue'], "invitees": invitee_details}
        preview_details["img"] = img
        html = t.render(RequestContext(request, {"preview_details": preview_details, "details": details, "invites": invites, "user_details": user_details}))

        return HttpResponse(html)

    raise Http404


def error_check(event):
    return HttpResponse(encoder.encode(1), mimetype='application/json')


def create(request):
    return HttpResponse


def event_creator_from_json(request):
    if not create_event(request):
        return HttpResponse(encoder.encode(0), mimetype='application/json')
    return HttpResponse(encoder.encode("something wrong happened, please refresh the page and try again"), mimetype='application/json')


def event_creator_from_html(request):
    create_event(request)
    return HttpResponseRedirect("/")


def create_event(request):
    if request.method == 'POST' and request.user.is_authenticated():
        form = EventCreatorForm(request.POST, request.FILES)

        if form.is_valid():
            event_data = form.cleaned_data.copy()
            event_data["user"] = request.user
            event_creator.submit_event(**event_data)
            return 0
        else:
            logger.error("form is invalid with %s" % form.errors)
            print "form errors with %s" % form.errors

    return 1


def cancel_event(request):
    if request.method == 'POST' and request.user.is_authenticated():
        event_time_id = request.POST.get("id")
        user = request.user
        if event_calculation.cancel_event(event_time_id, user):
            return HttpResponse(encoder.encode(0), mimetype='application/json')
    return HttpResponse(encoder.encode(1), mimetype='application/json')


def event_editor(request):
    if request.method == 'POST' and request.user.is_authenticated():
        form = EventEditorForm(request.POST, request.FILES)
        if form.is_valid():
            event_data = form.cleaned_data.copy()
            event_data["user"] = request.user
            if not event_calculation.edit_event(**event_data):
                return HttpResponse(encoder.encode(1), mimetype='application/json')
            else:
                return HttpResponse(encoder.encode(0), mimetype='application/json')
        else:
            logger.error("form is invalid with %s" % form.errors)

    return HttpResponse(encoder.encode(1), mimetype='application/json')


def get_notes(request):
    if request.method == 'GET':
        event_id = request.GET.get('id')
        user = request.user
        if event_id and request.user.is_authenticated():
            notes = note_calculation.notes_from_args(event_id, user)
            return HttpResponse(encoder.encode(notes), mimetype='application/json')

    return HttpResponse(encoder.encode(1), mimetype='application/json')


def share_note(request):
    if request.user.is_authenticated() and request.method == 'POST':
        note_id = request.POST.get("id")
        if note_id:
            note_calculation.share_note(note_id, request.user)
            return HttpResponse(encoder.encode(1), mimetype='application/json')

    return HttpResponse(encoder.encode(0), mimetype='application/json')


def share_detail(request):
    if request.user.is_authenticated():
        detail_id = request.POST.get("id")
        if detail_id:
            note_calculation.share_detail(detail_id, request.user)
            return HttpResponse(encoder.encode(1), mimetype='application/json')

    return HttpResponse(encoder.encode(0), mimetype='application/json')


def detail_creator(request):
    if request.method == 'POST' and request.user.is_authenticated():
        the_date = request.POST.get('eventDate')
        the_time = request.POST.get('eventTime')
        invitees = set(escape(x) for x in request.POST.getlist('who[]'))
        description = safe_get(request.POST, 'description')
        event_id = request.POST.get('eventId')
        user = request.user
        note_calculation.create_detail(
            the_date, the_time, description, user, invitees, event_id)
    return HttpResponse()


def discuss_creator(request):
    if request.method == 'POST' and request.user.is_authenticated():
        description = safe_get(request.POST, 'description')
        user = request.user
        invitees = set(escape(x) for x in request.POST.getlist('who[]'))
        event_id = request.POST.get('eventId')
        note_calculation.create_discuss(description, user, invitees, event_id)
    return HttpResponse()


def event_option(request):

    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/accounts/login/")
        else:
            event_id = request.POST.get('event')
            if not event_id:
                return HttpResponse(encoder.encode(1), mimetype='application/json')
            action = str(request.POST.get('action')).strip()
            event_calculation.make_a_change(request.user, action, event_id)
            return HttpResponse(encoder.encode(0), mimetype='application/json')
    else:
        raise Http404


def get_date(for_date):
    try:
        start_date = datetime.strptime(for_date, '%d%b%Y').date()
    except:
        start_date = datetime.strptime(for_date, '%Y%m%d').date()

    return start_date


def calc_for_date(for_date):
    page_details = {}

    if for_date:
        try:
            page_details["start_date"] = get_date(for_date)
            page_details["date_set"] = True
        except:
            logger.error(
                'invalid date %s passed into calc date func' % for_date)
            page_details["start_date"] = date.today()
            page_details["date_set"] = False
    else:
        page_details["start_date"] = date.today()
        page_details["date_set"] = False

    return page_details


def person_page(request, username, for_date=""):

    ''' displays the person page, this will be all the persons cals, all the
    person's tags, options to follow on twitter and a large picture of the
    person'''

    try:
        user = User.objects.get(username=username)
    except:
        raise Http404

    page_details = {}

    page_details["cal"] = username

    details = cal_calculation.get_person_details(user)
    t = get_template('index.html')
    html = t.render(RequestContext(
        request, {"details": details, "page_details": page_details}))

    return HttpResponse(html)


def series_page(request, series_id, for_date=""):
    """ displays the series page for all the events of that id """
    page_details = calc_for_date(for_date)
    t = get_template('index.html')
    html = t.render(RequestContext(request, {"page_details": page_details}))
    return HttpResponse(html)


def tag_page(request, tag_name, for_date=""):
    ''' displays the tag page, this will be all cals related to the tag, people
    who have applied this tag'''

    page_details = calc_for_date(for_date)
    page_details["tag"] = tag_name

    t = get_template('index.html')
    html = t.render(RequestContext(request, {"page_details": page_details}))

    return HttpResponse(html)


def search_term(request):
    form = EventQueryArgsValidation(request.GET, request.FILES)
    print form.errors

    if form.is_valid():
        args = form.cleaned_data
        event_holder = event_calculation.get_search_events(**args)
        response = encoder.encode(event_holder)
        return HttpResponse(response, mimetype='application/json')
    return HttpResponse(encoder.encode(1), mimetype='application/json')


def search(request):
    if not request.method == "GET":
        raise Http404

    t = get_template('index.html')
    params = {}
    params["date_set"] = False
    params["start_date"] = date.today()
    search_term = safe_get(request.GET, "search")
    if search_term:
        search_term.strip()
        params["search_term"] = search_term

    html = t.render(RequestContext(request, {"page_details": params}))
    return HttpResponse(html)


@authenticated
def main_page(request, for_date=False):
    page_details = calc_for_date(for_date)

    if not request.user.email:
        page_details["need_email"] = True

    t = get_template('index.html')
    html = t.render(RequestContext(request, {"page_details": page_details}))

    return HttpResponse(html)


def get_all_events(request):

    form = EventQueryArgsValidation(request.GET, request.FILES)
    if form.is_valid():
        args = form.cleaned_data
        if request.user.is_authenticated():
            args["user"] = request.user

        if "series" in args:
            results = event_calculation.calculate_series(**args)
        elif "cal" in args or "tag" in args:
            print "args are %s" % args
            results = event_calculation.calculate_specific(**args)
        else:
            print "args %s" % args
            results = event_calculation.calculate_stream(**args)

        return HttpResponse(encoder.encode(results), mimetype='application/json')
    else:
        print "errors %s" % form.errors
        logger.error("get all events form failed with %s" % form.errors)
        raise Http404


def get_cal_json(request):

    if request.method == 'POST':
        args = {}
        args["cal"] = request.POST.get("cal")
        args["string_post_date"] = request.POST.get("pageDate")
        args["string_last_date"] = request.POST.get("lastDate")
        args["string_last_time"] = request.POST.get("lastTime")
        args["tag"] = request.POST.get("tag")
        args["cal_type"] = request.POST.get("cal_type")

        if request.user.is_authenticated():
            login_user = request.user
        else:
            login_user = False

        user_tag, post_date, last_figg_date = event_validation.process_json_args(**args)
        cal_events = event_calculation.json_events(
            user_tag, post_date, last_figg_date, login_user)
        if request.user.is_authenticated():
            cal_calculation.add_viewed_calendar(
                user_tag, request.user.username)

    return HttpResponse(encoder.encode(cal_events), mimetype='application/json')


def page_not_found_404(request):
    return HttpResponse("Um something wrong has happened 404")

def page_not_found_500(request):
    return HttpResponse("Um something wrong has happened 500")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/l/starter")


def get_venues(request):
    if request.method == 'GET':
        startString = safe_get(request.GET, "startString")

        if startString:
            if request.user.is_authenticated():
                venues = venue_calculation.get_venues(
                    startString, request.user.username)
            else:
                venues = venue_calculation.get_venues(startString)
            return HttpResponse(encoder.encode(venues), mimetype='application/json')

    return HttpResponse(encoder.encode([]), mimetype='application/json')


def are_users(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            usernames = request.GET.getlist('uns[]')
            users = list(User.objects.filter(
                username__in=usernames).values_list("username", flat=True))
            return HttpResponse(encoder.encode(users), mimetype='application/json')

    return HttpResponse(encoder.encode([]), mimetype='application/json')


def get_users(request):
    if request.method == 'GET':
        startString = request.GET.get("startString")
        if(startString):
            query = "SELECT * FROM auth_user WHERE username LIKE '" + \
                startString + "%%'"
            users = map(
                lambda x: "%s" % x.username, User.objects.raw(query)[:8])
        else:
            users = map(lambda x: "%s" % x.username, User.objects.all()[:8])

        return HttpResponse(encoder.encode(users), mimetype='application/json')

    return HttpResponse(encoder.encode([]), mimetype='application/json')
